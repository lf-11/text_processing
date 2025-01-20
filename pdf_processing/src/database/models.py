from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey
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