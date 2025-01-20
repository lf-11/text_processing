# Files with more than 100 lines

- **processor.py** (src/pdf_processing/processor.py): 442 lines
- **text_analysis.py** (src/pdf_processing/text_analysis.py): 169 lines
- **app.py** (src/web/app.py): 185 lines
- **analysis.css** (src/web/static/css/analysis.css): 248 lines
- **pdf_analysis_view.css** (src/web/static/css/pdf_analysis_view.css): 122 lines
- **viewer.css** (src/web/static/css/viewer.css): 130 lines
- **analysis.html** (src/web/templates/analysis.html): 108 lines

# Project Structure
├── .env
├── .gitignore
├── file_structure.py
├── pdf_processing.egg-info
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── requires.txt
│   ├── top_level.txt
├── pdfs
├── project_structure.md
├── requirements.txt
├── scripts
│   ├── __init__.py
│   ├── process_pdf.py
│   ├── setup_db.py
├── setup.py
├── src
│   ├── config
│   │   ├── settings.py
│   ├── database
│   │   ├── connection.py
│   │   ├── models.py
│   ├── pdf_processing
│   │   ├── models.py
│   │   ├── processor.py
│   │   ├── text_analysis.py
│   ├── web
│   │   ├── app.py
│   │   ├── static
│   │   │   ├── css
│   │   │   │   ├── analysis.css
│   │   │   │   ├── base.css
│   │   │   │   ├── documents.css
│   │   │   │   ├── pdf_analysis_view.css
│   │   │   │   ├── styles.css
│   │   │   │   ├── viewer.css
│   │   │   ├── js
│   │   │   │   ├── viewer.js
│   │   ├── templates
│   │   │   ├── analysis.html
│   │   │   ├── base.html
│   │   │   ├── document_list.html
│   │   │   ├── pdf_analysis_view.html
│   │   │   ├── viewer.html
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_data
│   ├── test_pdf_processing