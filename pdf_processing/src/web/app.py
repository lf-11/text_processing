from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
from fastapi.responses import Response
from starlette.responses import StreamingResponse
import mimetypes

from src.database.connection import get_db
from src.database.models import Document, TextBlock
from src.config.settings import PDF_FOLDER, BASE_DIR

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "src", "web", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

@app.get("/")
async def list_documents(request: Request, db: Session = Depends(get_db)):
    documents = db.query(Document).all()
    return templates.TemplateResponse(
        "document_list.html",
        {"request": request, "documents": documents}
    )

@app.get("/view/{document_id}")
async def view_document(request: Request, document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    text_blocks = db.query(TextBlock)\
        .filter(TextBlock.document_id == document_id)\
        .order_by(TextBlock.page_number, TextBlock.bbox_coordinates['y0'].asc())\
        .all()
    
    # Group blocks by page
    pages = {}
    for block in text_blocks:
        if block.page_number not in pages:
            pages[block.page_number] = []
        pages[block.page_number].append(block)
    
    return templates.TemplateResponse(
        "viewer.html",
        {
            "request": request,
            "document": document,
            "pages": pages,
            "pdf_path": f"/pdf/{document_id}"
        }
    )

@app.get("/pdf/{document_id}")
async def get_pdf(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    if not os.path.exists(document.file_path):
        raise HTTPException(
            status_code=404, 
            detail="PDF file not found on disk"
        )

    def iterfile():
        with open(document.file_path, 'rb') as f:
            yield from f

    # Use a simple filename without special characters
    safe_filename = f"document_{document_id}.pdf"

    return StreamingResponse(
        iterfile(),
        media_type="application/pdf",
        headers={
            'Content-Disposition': f'inline; filename="{safe_filename}"',
            'Accept-Ranges': 'bytes'
        }
    ) 