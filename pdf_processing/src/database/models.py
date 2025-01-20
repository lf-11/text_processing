from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True)
    file_path = Column(String, nullable=False)
    processed_at = Column(DateTime, nullable=False)
    file_name = Column(String, nullable=False)
    strategy = Column(String, nullable=False)

class TextBlock(Base):
    __tablename__ = "text_blocks"

    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    text_content = Column(String, nullable=False)
    bbox_coordinates = Column(JSON, nullable=False)
    font_size = Column(Float, nullable=False)
    font_name = Column(String, nullable=False)
    font_color = Column(String, nullable=False)
    block_type = Column(String, nullable=False)

class DocumentAnalysis(Base):
    __tablename__ = "document_analyses"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    analysis_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class StyleStatistics(Base):
    __tablename__ = "style_statistics"
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    font_name = Column(String, nullable=False)
    font_size = Column(Float, nullable=False)
    font_color = Column(String, nullable=False)
    is_bold = Column(Boolean, default=False)
    is_italic = Column(Boolean, default=False)
    is_underlined = Column(Boolean, default=False)
    occurrence_count = Column(Integer, nullable=False)
    examples = Column(JSON, nullable=True)  # Store text examples
    page_distribution = Column(JSON, nullable=True)  # Store page numbers
    y_range = Column(JSON, nullable=True)  # Store y coordinate range
    x_range = Column(JSON, nullable=True)  # Store x coordinate range