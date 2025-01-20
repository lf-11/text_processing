from src.pdf_processing.processor import PDFProcessor
from src.database.connection import SessionLocal
import os
from src.config.settings import PDF_FOLDER
import argparse

def process_single_pdf(file_name: str, strategy: str = "dict"):
    file_path = os.path.join(PDF_FOLDER, file_name)
    processor = PDFProcessor(file_path, strategy)
    document, text_blocks = processor.process_document()
    
    # Save to database
    db = SessionLocal()
    try:
        # Save document first to get its ID
        db.add(document)
        db.flush()
        
        # Set document_id for all text blocks and save them
        for block in text_blocks:
            block.document_id = document.id
            db.add(block)
        
        db.commit()
        print(f"Successfully processed {file_name} using {strategy} strategy")
        
    except Exception as e:
        db.rollback()
        print(f"Error processing {file_name}: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process PDF files with different strategies')
    parser.add_argument('--strategy', type=str, default='dict',
                       choices=['dict', 'blocks', 'words'],
                       help='Text extraction strategy to use')
    args = parser.parse_args()
    
    # Process first PDF in the folder as a test
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    if pdf_files:
        process_single_pdf(pdf_files[0], args.strategy) 