from setuptools import setup, find_packages

setup(
    name="pdf_processing",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pymupdf",
        "psycopg2-binary",
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "pytest",
        "sqlalchemy",
    ],
) 