from fastapi import APIRouter, UploadFile
from docx2pdf import convert

import os
import json
import time
import uuid
import tempfile
import subprocess
from io import BytesIO
from docxtpl import DocxTemplate
#from html_to_docx import html_to_docx

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "generated", "pdf")
os.makedirs(OUTPUT_DIR, exist_ok=True)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GENERATED_DIR = os.path.join(BASE_DIR, "app", "generated")
PDF_DIR = os.path.join(GENERATED_DIR, "pdf")
DOCX_DIR = os.path.join(GENERATED_DIR, "docx")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(DOCX_DIR, exist_ok=True)

def get_soffice_path():
    # Windows / Linux compatible
    return "soffice"

@router.post("/to-pdf")
async def docx_to_pdf(file: UploadFile):
    file_id = str(uuid.uuid4())

    docx_path = os.path.join(OUTPUT_DIR, f"{file_id}.docx")
    pdf_path = os.path.join(OUTPUT_DIR, f"{file_id}.pdf")

    print("DOCX PATH = ",docx_path)
    print("PDF PATH = ", docx_path)
    # save uploaded docx
    with open(docx_path, "wb") as f:
        f.write(await file.read())

    # convert
    convert(docx_path, pdf_path)

    return {
        "status": "success",
        "pdf_path": pdf_path
    }
