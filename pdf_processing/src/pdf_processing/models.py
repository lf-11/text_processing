from dataclasses import dataclass
from typing import List

@dataclass
class TextSpan:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    font_name: str
    font_size: float
    font_color: str
    is_bold: bool
    is_italic: bool
    is_underlined: bool
    page_number: int = 1

@dataclass
class TextLine:
    spans: List[TextSpan]
    y0: float
    y1: float
    x0: float
    x1: float 