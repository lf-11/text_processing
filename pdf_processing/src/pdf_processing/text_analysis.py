from collections import defaultdict
from typing import List, Dict, Any
from statistics import mean, stdev
from src.pdf_processing.models import TextSpan, TextLine

class TextAnalyzer:
    def __init__(self):
        self.style_stats = defaultdict(lambda: {
            'count': 0,
            'examples': [],
            'page_occurrences': set(),
            'y_coords': [],
            'x_coords': []
        })
        self.line_width_stats = []
        self.margin_stats = []
        
    def analyze_spans(self, spans: List[TextSpan]) -> Dict[str, Any]:
        """Analyze text spans and collect statistics"""
        # Reset statistics for new analysis
        self.style_stats.clear()
        self.line_width_stats.clear()
        self.margin_stats.clear()
        
        # Group spans by approximate y-coordinate
        lines = self._group_into_lines(spans)
        
        # Collect style statistics
        for span in spans:
            try:
                style_key = (
                    str(span.font_name),
                    float(span.font_size),
                    str(span.font_color),
                    bool(span.is_bold),
                    bool(span.is_italic),
                    bool(span.is_underlined)
                )
                
                # Update statistics
                stats = self.style_stats[style_key]
                stats['count'] += 1
                
                # Store example text (limit to 100 chars)
                if len(span.text.strip()) > 3:  # Only store meaningful examples
                    if len(stats['examples']) < 3:  # Store up to 3 examples
                        stats['examples'].append(span.text[:100])
                
                # Store coordinates
                stats['y_coords'].append(span.y0)
                stats['x_coords'].append(span.x0)
                
                # Store page number if available
                if hasattr(span, 'page_number'):
                    stats['page_occurrences'].add(span.page_number)
                
            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping span due to invalid data: {e}")
                continue
        
        # Analyze line patterns
        for line in lines:
            try:
                width = float(line.x1 - line.x0)
                margin = float(line.x0)
                self.line_width_stats.append(width)
                self.margin_stats.append(margin)
            except (ValueError, TypeError) as e:
                print(f"Warning: Skipping line metrics due to invalid data: {e}")
                continue
        
        return self._generate_analysis_report()
    
    def _group_into_lines(self, spans: List[TextSpan], y_tolerance: float = 3) -> List[TextLine]:
        """Group spans into lines based on y-coordinates"""
        # Sort spans by y0 coordinate
        sorted_spans = sorted(spans, key=lambda s: (s.y0, s.x0))
        lines = []
        current_line = []
        current_y = None
        
        for span in sorted_spans:
            if current_y is None:
                current_y = span.y0
                
            if abs(span.y0 - current_y) <= y_tolerance:
                current_line.append(span)
            else:
                if current_line:
                    lines.append(self._create_line(current_line))
                current_line = [span]
                current_y = span.y0
                
        if current_line:
            lines.append(self._create_line(current_line))
            
        return lines
    
    def _create_line(self, spans: List[TextSpan]) -> TextLine:
        """Create a TextLine from a list of spans"""
        return TextLine(
            spans=spans,
            y0=min(s.y0 for s in spans),
            y1=max(s.y1 for s in spans),
            x0=min(s.x0 for s in spans),
            x1=max(s.x1 for s in spans)
        )
    
    def _generate_analysis_report(self) -> Dict[str, Any]:
        """Generate statistical report from collected data"""
        try:
            # Calculate common line widths
            avg_width = mean(self.line_width_stats) if self.line_width_stats else 0.0
            width_std = stdev(self.line_width_stats) if len(self.line_width_stats) > 1 else 0.0
            avg_margin = mean(self.margin_stats) if self.margin_stats else 0.0
            
            # Sort style statistics
            sorted_styles = sorted(
                self.style_stats.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )
            
            # Create common styles list with explicit type conversion
            common_styles = []
            for style, stats in sorted_styles[:10]:  # Top 10 most common styles
                try:
                    style_dict = {
                        "font_name": str(style[0]),
                        "font_size": float(style[1]),
                        "font_color": str(style[2]),
                        "is_bold": bool(style[3]),
                        "is_italic": bool(style[4]),
                        "is_underlined": bool(style[5]),
                        "count": int(stats['count']),
                        "examples": stats['examples'],
                        "page_distribution": sorted(stats['page_occurrences']),
                        "y_range": {
                            "min": min(stats['y_coords']),
                            "max": max(stats['y_coords'])
                        },
                        "x_range": {
                            "min": min(stats['x_coords']),
                            "max": max(stats['x_coords'])
                        }
                    }
                    common_styles.append(style_dict)
                except (IndexError, ValueError, TypeError) as e:
                    print(f"Warning: Skipping style due to invalid data: {e}")
                    continue
            
            return {
                "common_styles": common_styles,
                "line_metrics": {
                    "average_width": float(avg_width),
                    "width_std": float(width_std),
                    "average_left_margin": float(avg_margin)
                }
            }
        except Exception as e:
            print(f"Error generating analysis report: {e}")
            return {
                "common_styles": [],
                "line_metrics": {
                    "average_width": 0.0,
                    "width_std": 0.0,
                    "average_left_margin": 0.0
                }
            } 