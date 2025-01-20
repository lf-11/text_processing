from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from fastapi.responses import Response
from starlette.responses import StreamingResponse
import mimetypes

from src.database.connection import get_db
from src.database.models import Document, TextBlock, DocumentAnalysis, StyleStatistics
from src.config.settings import PDF_FOLDER, BASE_DIR
from src.pdf_processing.processor import PDFProcessor

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "src", "web", "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "src", "web", "templates"))

# Create a template filter to generate highlight colors
def highlight_color(index: int) -> str:
    """Generate a highlight color based on index"""
    colors = [
        "#fff176",  # Light yellow
        "#81c784",  # Light green
        "#ff8a65",  # Light red
        "#64b5f6",  # Light blue
        "#ba68c8",  # Light purple
        "#4db6ac",  # Light teal
        "#ff8a80",  # Light coral
        "#90caf9",  # Another light blue
        "#ce93d8",  # Another light purple
        "#80cbc4",  # Another light teal
    ]
    return colors[index % len(colors)]

# Add the filter to Jinja2 templates
templates.env.filters["highlight_color"] = highlight_color

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
        .order_by(
            TextBlock.page_number,
            text("(bbox_coordinates->>'y0')::float")
        )\
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

@app.get("/analysis/{document_id}")
async def view_analysis(request: Request, document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    analysis = db.query(DocumentAnalysis)\
        .filter(DocumentAnalysis.document_id == document_id)\
        .first()
    
    style_stats = db.query(StyleStatistics)\
        .filter(StyleStatistics.document_id == document_id)\
        .all()
    
    return templates.TemplateResponse(
        "analysis.html",
        {
            "request": request,
            "document": document,
            "analysis": analysis,
            "style_stats": style_stats
        }
    )

@app.get("/analysis/{document_id}/highlighted-pdf")
async def get_highlighted_pdf(document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    style_stats = db.query(StyleStatistics)\
        .filter(StyleStatistics.document_id == document_id)\
        .all()
    
    # Create processor with analysis strategy
    processor = PDFProcessor(document.file_path, "analysis")
    
    # Generate highlighted PDF
    output_path = os.path.join(
        PDF_FOLDER,
        f"highlighted_{document_id}.pdf"
    )
    
    try:
        processor.strategy.create_highlighted_pdf(processor.doc, output_path, style_stats)
        
        return StreamingResponse(
            open(output_path, "rb"),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="highlighted_{document_id}.pdf"'
            }
        )
    finally:
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)

@app.get("/analysis/{document_id}/view-highlighted")
async def view_highlighted_pdf(request: Request, document_id: int, db: Session = Depends(get_db)):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    style_stats = db.query(StyleStatistics)\
        .filter(StyleStatistics.document_id == document_id)\
        .all()
    
    return templates.TemplateResponse(
        "pdf_analysis_view.html",
        {
            "request": request,
            "document": document,
            "style_stats": style_stats
        }
    ) 