from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database settings
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/pdf_processing"

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent

PDF_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "pdfs")