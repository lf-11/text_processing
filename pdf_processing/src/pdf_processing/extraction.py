import fitz
import re
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from src.pdf_processing.models import TextSpan
from src.pdf_processing.text_analysis import TextAnalyzer

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
        if y_position > page_height * 0.85 and font_size <= 9:
            return "footnote"
        elif font_size >= 14:
            return "headline"
        return "body"
    
    def _clean_text(self, text: str) -> str:
        """Clean up text artifacts"""
        text = re.sub(r'(.)\1', r'\1', text)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'([IVX]+)\.+', r'\1.', text)
        return text.strip()

class DictMethodStrategy(TextExtractionStrategy):
    """Strategy using the 'dict' method from PyMuPDF"""
    
    def extract_text(self, page: fitz.Page) -> List[Dict[str, Any]]:
        blocks_data = []
        dict_blocks = page.get_text("dict")["blocks"]
        page_height = page.rect.height
        
        # Sort blocks by y-position to maintain layout order
        dict_blocks.sort(key=lambda b: (b["bbox"][1], b["bbox"][0]))
        
        for block in dict_blocks:
            if "lines" not in block:
                continue
            
            # Extract text content from all lines in the block
            text_content = " ".join(
                span["text"] for line in block["lines"] 
                for span in line["spans"]
            )
            
            # Skip empty blocks
            if not text_content.strip():
                continue
            
            # Get the first span's properties
            first_span = block["lines"][0]["spans"][0]
            y_position = block["bbox"][1]
            
            # Clean up text content
            text_content = self._clean_text(text_content)
            
            blocks_data.append({
                "text_content": text_content,
                "bbox_coordinates": {
                    "x0": block["bbox"][0],
                    "y0": block["bbox"][1],
                    "x1": block["bbox"][2],
                    "y1": block["bbox"][3]
                },
                "font_size": first_span["size"],
                "font_name": first_span["font"],
                "font_color": self._get_color_string(first_span.get("color")),
                "block_type": self._determine_block_type(
                    first_span["size"], 
                    y_position, 
                    page_height
                )
            })
        
        return blocks_data

class BlocksMethodStrategy(TextExtractionStrategy):
    """Strategy using the 'blocks' method from PyMuPDF"""
    
    def extract_text(self, page: fitz.Page) -> List[Dict[str, Any]]:
        blocks_data = []
        raw_blocks = page.get_text("blocks", sort=True)
        
        for block in raw_blocks:
            # block format: (x0, y0, x1, y1, "text", block_no, block_type)
            x0, y0, x1, y1, text, _, _ = block
            
            # For this method, we don't have direct access to font properties
            # We could use page.get_text("dict") specifically for getting font info
            # of this block's coordinates, but for now we'll use defaults
            blocks_data.append({
                "text_content": text,
                "bbox_coordinates": {
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1
                },
                "font_size": 12,  # default size
                "font_name": "default",
                "font_color": "#000000",
                "block_type": "body"  # default type
            })
        
        return blocks_data

class WordsMethodStrategy(TextExtractionStrategy):
    """Strategy using the 'words' method from PyMuPDF"""
    
    def extract_text(self, page: fitz.Page) -> List[Dict[str, Any]]:
        blocks_data = []
        words = page.get_text("words", sort=True)
        page_height = page.rect.height
        
        current_block = self._create_empty_block()
        
        for word in words:
            x0, y0, x1, y1, text, block_no, line_no, _ = word
            
            # Start new block if block number changes or significant y-position change
            if (current_block["block_no"] is not None and 
                (current_block["block_no"] != block_no or 
                 abs(y0 - current_block["y0"]) > 20)):  # Adjust threshold as needed
                
                if current_block["text"]:
                    blocks_data.append(self._create_block_data(
                        current_block, page_height
                    ))
                current_block = self._create_empty_block()
            
            # Update current block
            current_block["text"].append(text)
            current_block["x0"] = min(current_block["x0"], x0)
            current_block["y0"] = min(current_block["y0"], y0)
            current_block["x1"] = max(current_block["x1"], x1)
            current_block["y1"] = max(current_block["y1"], y1)
            current_block["block_no"] = block_no
            current_block["line_no"] = line_no
        
        # Don't forget to add the last block
        if current_block["text"]:
            blocks_data.append(self._create_block_data(current_block, page_height))
        
        return blocks_data
    
    def _create_empty_block(self) -> Dict:
        return {
            "text": [],
            "x0": float('inf'),
            "y0": float('inf'),
            "x1": float('-inf'),
            "y1": float('-inf'),
            "block_no": None,
            "line_no": None
        }
    
    def _create_block_data(self, block: Dict, page_height: float) -> Dict[str, Any]:
        """Create a standardized block data dictionary from accumulated words"""
        # Clean up text content
        text_content = self._clean_text(" ".join(block["text"]))
        
        return {
            "text_content": text_content,
            "bbox_coordinates": {
                "x0": block["x0"],
                "y0": block["y0"],
                "x1": block["x1"],
                "y1": block["y1"]
            },
            "font_size": 12,  # default size
            "font_name": "default",
            "font_color": "#000000",
            "block_type": self._determine_block_type(
                12,  # default font size
                block["y0"],
                page_height
            )
        } 