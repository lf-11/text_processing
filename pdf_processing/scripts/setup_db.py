import psycopg2
from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config.settings import DATABASE_URL

def setup_database():
    load_dotenv()
    
    # Connect to PostgreSQL using the URL from settings
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    
    # Drop existing tables if they exist
    cur.execute('''
        DROP TABLE IF EXISTS text_blocks;
        DROP TABLE IF EXISTS documents;
    ''')
    
    # Create tables
    cur.execute('''
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            file_path TEXT NOT NULL,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_name TEXT NOT NULL,
            strategy TEXT NOT NULL
        );
        
        CREATE TABLE text_blocks (
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
    
    print("Database tables recreated successfully")

if __name__ == "__main__":
    setup_database()