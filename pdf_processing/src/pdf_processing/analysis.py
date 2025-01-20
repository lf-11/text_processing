import fitz
from typing import List, Dict, Any, Tuple
from src.database.models import StyleStatistics
from src.pdf_processing.extraction import TextExtractionStrategy
from src.pdf_processing.models import TextSpan
from src.pdf_processing.text_analysis import TextAnalyzer

class TextAnalysisStrategy(TextExtractionStrategy):
    """Strategy using detailed span-level analysis"""
    
    def __init__(self):
        super().__init__()
        self.analyzer = TextAnalyzer()
    
    def _get_font_flags(self, flags: int) -> tuple[bool, bool, bool]:
        """Extract boolean font style flags from the flags integer"""
        if flags is None:
            return False, False, False
            
        # PyMuPDF font flags
        is_bold = bool(flags & 2**4)  # 16
        is_italic = bool(flags & 2**1)  # 2
        is_underlined = bool(flags & 2**2)  # 4
        
        return is_bold, is_italic, is_underlined
        
    def extract_text(self, page: fitz.Page) -> List[Dict[str, Any]]:
        spans = []
        dict_page = page.get_text("dict")
        
        for block in dict_page["blocks"]:
            if "lines" not in block:
                continue
                
            for line in block["lines"]:
                for span in line["spans"]:
                    flags = span.get("flags", 0)
                    is_bold, is_italic, is_underlined = self._get_font_flags(flags)
                    
                    text_span = TextSpan(
                        text=span["text"],
                        x0=span["bbox"][0],
                        y0=span["bbox"][1],
                        x1=span["bbox"][2],
                        y1=span["bbox"][3],
                        font_name=span["font"],
                        font_size=span["size"],
                        font_color=self._get_color_string(span.get("color")),
                        is_bold=is_bold,
                        is_italic=is_italic,
                        is_underlined=is_underlined,
                        page_number=page.number + 1
                    )
                    spans.append(text_span)
        
        # Convert spans to standard block format
        blocks_data = []
        lines = self.analyzer._group_into_lines(spans)
        
        for line in lines:
            main_span = max(line.spans, key=lambda s: len(s.text))
            
            blocks_data.append({
                "text_content": " ".join(span.text for span in line.spans),
                "bbox_coordinates": {
                    "x0": line.x0,
                    "y0": line.y0,
                    "x1": line.x1,
                    "y1": line.y1
                },
                "font_size": main_span.font_size,
                "font_name": main_span.font_name,
                "font_color": main_span.font_color,
                "block_type": self._determine_block_type(
                    main_span.font_size,
                    line.y0,
                    page.rect.height
                ),
                "_spans": spans  # Pass spans for later analysis
            })
        
        return blocks_data

    def _generate_highlight_colors(self, num_styles: int) -> List[tuple]:
        """Generate distinct highlight colors (bright, marker-like colors)"""
        highlight_colors = [
            (1, 0.9, 0),        # Stronger yellow
            (0.3, 1, 0.3),      # Brighter green
            (1, 0.5, 0.5),      # Stronger pink
            (0.5, 0.7, 1),      # Stronger blue
            (1, 0.6, 0),        # Stronger orange
            (0, 0.8, 0.8),      # Stronger cyan
            (1, 0.4, 1),        # Stronger magenta
            (0.8, 1, 0),        # Stronger lime
            (1, 0.7, 0.4),      # Stronger peach
            (0.4, 0.8, 1)       # Stronger sky blue
        ]
        
        # If we need more colors than predefined, cycle through them
        return [highlight_colors[i % len(highlight_colors)] for i in range(num_styles)]

    def create_highlighted_pdf(self, doc: fitz.Document, output_path: str, style_stats: List[StyleStatistics]) -> str:
        """Create a new PDF with highlighted text styles"""
        doc_out = fitz.open()
        colors = self._generate_highlight_colors(len(style_stats))
        style_colors = {}
        
        # Create mapping of style characteristics to colors
        for style, color in zip(style_stats, colors):
            style_key = (
                style.font_name,
                style.font_size,
                style.font_color,
                style.is_bold,
                style.is_italic
            )
            style_colors[style_key] = color
        
        # Process each page
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_out = doc_out.new_page(width=page.rect.width, height=page.rect.height)
            
            # Copy original page content
            page_out.show_pdf_page(page.rect, doc, page_num)
            
            # Get text spans
            dict_page = page.get_text("dict")
            
            # Add highlights for each text span
            for block in dict_page["blocks"]:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        flags = span.get("flags", 0)
                        is_bold, is_italic, _ = self._get_font_flags(flags)
                        
                        style_key = (
                            span["font"],
                            span["size"],
                            self._get_color_string(span.get("color")),
                            is_bold,
                            is_italic
                        )
                        
                        if style_key in style_colors:
                            highlight_color = style_colors[style_key]
                            rect = fitz.Rect(span["bbox"])
                            page_out.draw_rect(
                                rect,
                                color=None,  # No border
                                fill=highlight_color,
                                fill_opacity=0.3
                            )
        
        # Save the highlighted PDF
        doc_out.save(output_path)
        doc_out.close()
        return output_path 