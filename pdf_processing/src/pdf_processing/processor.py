import fitz  # PyMuPDF
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Protocol
from abc import ABC, abstractmethod
from src.database.models import Document, TextBlock, DocumentAnalysis, StyleStatistics
from src.config.settings import PDF_FOLDER
from src.pdf_processing.models import TextSpan
from src.pdf_processing.text_analysis import TextAnalyzer
from src.pdf_processing.extraction import DictMethodStrategy, BlocksMethodStrategy, WordsMethodStrategy
from src.pdf_processing.analysis import TextAnalysisStrategy

class TextExtractionStrategy(ABC):
    """Abstract base class for different text extraction strategies"""
    
    @abstractmethod
    def extract_text(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract text blocks from a page and return list of block data"""
        pass
    
    def _get_color_string(self, color) -> str:
        """Convert color value to hex string."""
        if not color:
            return "#000000"
        return f"#{color:06x}" if isinstance(color, int) else str(color)
    
    def _determine_block_type(self, font_size: float, y_position: float, page_height: float) -> str:
        """Determine block type based on font size and position"""
        # Consider text in the bottom 15% of page as potential footnotes
        if y_position > page_height * 0.85 and font_size <= 9:
            return "footnote"
        elif font_size >= 14:
            return "headline"
        return "body"
    
    def _clean_text(self, text: str) -> str:
        """Clean up text artifacts"""
        # Remove repeated characters (e.g., "EEiinnlleeiittuunngg" -> "Einleitung")
        text = re.sub(r'(.)\1', r'\1', text)
        
        # Fix common OCR artifacts
        text = re.sub(r'\.{2,}', '.', text)  # Multiple dots to single dot
        text = re.sub(r'\s+', ' ', text)     # Multiple spaces to single space
        
        # Clean up Roman numerals (e.g., "II.." -> "II.")
        text = re.sub(r'([IVX]+)\.+', r'\1.', text)
        
        return text.strip()

class PDFProcessor:
    """Main processor class that uses different extraction strategies"""
    
    STRATEGIES = {
        "dict": DictMethodStrategy(),
        "blocks": BlocksMethodStrategy(),
        "words": WordsMethodStrategy(),
        "analysis": TextAnalysisStrategy(),
    }
    
    def __init__(self, file_path: str, strategy_name: str = "dict"):
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.strategy = self.STRATEGIES.get(strategy_name)
        if not self.strategy:
            raise ValueError(f"Unknown strategy: {strategy_name}. "
                           f"Available strategies: {list(self.STRATEGIES.keys())}")
    
    def process_document(self) -> tuple[Document, List[TextBlock]]:
        """Process a PDF document and return Document and TextBlock instances."""
        document = Document(
            id=None,
            file_path=self.file_path,
            processed_at=datetime.now(),
            file_name=os.path.basename(self.file_path),
            strategy=self.strategy.__class__.__name__.replace('Strategy', '').lower()
        )
        
        text_blocks = []
        all_spans = []  # For analysis strategy
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks_data = self.strategy.extract_text(page)
            
            for block_data in blocks_data:
                # Extract spans if present (for analysis strategy)
                if isinstance(self.strategy, TextAnalysisStrategy):
                    if '_spans' in block_data:
                        all_spans.extend(block_data.pop('_spans'))
                
                text_block = TextBlock(
                    id=None,
                    document_id=None,
                    page_number=page_num + 1,
                    **block_data
                )
                text_blocks.append(text_block)
        
        # Generate analysis after processing all pages
        if isinstance(self.strategy, TextAnalysisStrategy) and all_spans:
            analysis_data = self.strategy.analyzer.analyze_spans(all_spans)
            document_analysis = DocumentAnalysis(
                document_id=None,
                analysis_data=analysis_data
            )
            
            style_stats = []
            for style in analysis_data['common_styles']:
                stat = StyleStatistics(
                    document_id=None,
                    font_name=style['font_name'],
                    font_size=style['font_size'],
                    font_color=style['font_color'],
                    is_bold=style['is_bold'],
                    is_italic=style['is_italic'],
                    is_underlined=style['is_underlined'],
                    occurrence_count=style['count'],
                    examples=style.get('examples', []),
                    page_distribution=style.get('page_distribution', []),
                    y_range=style.get('y_range', {'min': 0, 'max': 0}),
                    x_range=style.get('x_range', {'min': 0, 'max': 0})
                )
                style_stats.append(stat)
            
            return document, text_blocks, document_analysis, style_stats
        
        return document, text_blocks
    
    def __del__(self):
        if hasattr(self, 'doc'):
            self.doc.close()