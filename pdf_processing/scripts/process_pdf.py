import os
import sys

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.pdf_processing.processor import PDFProcessor, TextAnalysisStrategy
from src.database.connection import SessionLocal
from src.config.settings import PDF_FOLDER
import argparse

def process_single_pdf(file_name: str, strategy: str = "dict"):
    file_path = os.path.join(PDF_FOLDER, file_name)
    processor = PDFProcessor(file_path, strategy)
    result = processor.process_document()
    
    # Save to database
    db = SessionLocal()
    try:
        # Handle different return types based on strategy
        if isinstance(processor.strategy, TextAnalysisStrategy):
            document, text_blocks, document_analysis, style_stats = result
        else:
            document, text_blocks = result
        
        # Save document first to get its ID
        db.add(document)
        db.flush()
        
        # Set document_id for all text blocks and save them
        for block in text_blocks:
            block.document_id = document.id
            db.add(block)
        
        # If using analysis strategy, save analysis data
        if isinstance(processor.strategy, TextAnalysisStrategy):
            document_analysis.document_id = document.id
            db.add(document_analysis)
            
            # Save style statistics
            for stat in style_stats:
                stat.document_id = document.id
                db.add(stat)
        
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
                       choices=['dict', 'blocks', 'words', 'analysis'],
                       help='Text extraction strategy to use')
    parser.add_argument('--mode', type=str, default='single',
                       choices=['single', 'all'],
                       help='Process single file or all files')
    parser.add_argument('--filename', type=str,
                       help='Specific PDF file to process (optional)')
    args = parser.parse_args()
    
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    if not pdf_files:
        print(f"No PDF files found in {PDF_FOLDER}")
        sys.exit(1)

    if args.mode == 'single':
        # If filename is provided, process that specific file
        if args.filename:
            if args.filename in pdf_files:
                process_single_pdf(args.filename, args.strategy)
            else:
                print(f"File {args.filename} not found in {PDF_FOLDER}")
        else:
            # If no filename provided, process the first PDF in the folder
            print(f"Processing first file: {pdf_files[0]}")
            process_single_pdf(pdf_files[0], args.strategy)
    else:  # mode == 'all'
        print(f"Processing all {len(pdf_files)} PDF files...")
        for pdf_file in pdf_files:
            print(f"\nProcessing {pdf_file}...")
            process_single_pdf(pdf_file, args.strategy)
        print("\nCompleted processing all files!") 