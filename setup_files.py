import os
import pathlib

def create_file(path: str, content: str = "") -> None:
    """Create a file with optional content."""
    with open(path, 'w') as f:
        f.write(content)

def setup_project():
    # Define base directory
    base_dir = pathlib.Path("text_processing")
    
    # Create main project directories
    directories = [
        "src",
        "src/config",
        "src/database",
        "src/pdf_processing",
        "src/web",
        "src/web/static/css",
        "src/web/static/js",
        "src/web/templates",
        "tests",
        "tests/test_pdf_processing",
        "tests/test_data",
        "scripts"
    ]
    
    # Create directories
    for dir_path in directories:
        os.makedirs(base_dir / dir_path, exist_ok=True)
    
    # Create __init__.py files
    init_paths = [
        "src",
        "src/config",
        "src/database",
        "src/pdf_processing",
        "src/web",
        "tests",
    ]
    for init_path in init_paths:
        create_file(base_dir / init_path / "__init__.py")
    
    # Create basic files with minimal content
    files = {
        ".env": "DATABASE_URL=postgresql://user:password@localhost:5432/text_processing\n",
        
        ".gitignore": """
__pycache__/
*.py[cod]
*$py.class
.env
.venv
env/
venv/
ENV/
*.pdf
""",
        
        "requirements.txt": """
pymupdf==1.23.8
psycopg2-binary==2.9.9
fastapi==0.109.0
uvicorn==0.27.0
python-dotenv==1.0.0
pytest==7.4.4
""",
        
        "src/config/settings.py": """
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database settings
DATABASE_URL = os.getenv('DATABASE_URL')

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
""",
        
        "src/database/models.py": """
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Document:
    id: Optional[int]
    file_path: str
    processed_at: datetime
    file_name: str

@dataclass
class TextBlock:
    id: Optional[int]
    document_id: int
    page_number: int
    text_content: str
    bbox_coordinates: dict
    font_size: float
    font_name: str
    font_color: str
    block_type: str
""",
        
        "src/pdf_processing/processor.py": """
from fitz import Document
from typing import Dict, List
import psycopg2

class PDFProcessor:
    def __init__(self, db_connection_string: str):
        self.conn = psycopg2.connect(db_connection_string)
    
    def process_document(self, file_path: str) -> int:
        '''Process PDF document and store in database'''
        pass
""",
        
        "scripts/setup_db.py": """
import psycopg2
from dotenv import load_dotenv
import os

def setup_database():
    load_dotenv()
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    
    # Create tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            file_path TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_name TEXT NOT NULL
        );
        
        CREATE TABLE IF NOT EXISTS text_blocks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id),
            page_number INTEGER NOT NULL,
            text_content TEXT NOT NULL,
            bbox_coordinates JSONB,
            font_size FLOAT,
            font_name TEXT,
            font_color TEXT,
            block_type TEXT
        );
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    setup_database()
""",
        
        "tests/conftest.py": """
import pytest
import psycopg2
from dotenv import load_dotenv
import os

@pytest.fixture
def db_connection():
    load_dotenv()
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    yield conn
    conn.close()
"""
    }
    
    for file_path, content in files.items():
        create_file(base_dir / file_path, content.strip())

if __name__ == "__main__":
    setup_project()
    print("Project structure created successfully!")
