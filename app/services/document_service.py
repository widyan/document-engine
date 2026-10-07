import os
import json
import time
import uuid
import tempfile
import subprocess
from io import BytesIO
from docxtpl import DocxTemplate

# =====================
# PATH CONFIG
# =====================
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GENERATED_DIR = os.path.join(BASE_DIR, "app", "generated")
PDF_DIR = os.path.join(GENERATED_DIR, "pdf")
DOCX_DIR = os.path.join(GENERATED_DIR, "docx")

os.makedirs(PDF_DIR, exist_ok=True)
os.makedirs(DOCX_DIR, exist_ok=True)


# =====================
# LIBREOFFICE
# =====================
def get_soffice():
    paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError("LibreOffice not found")

    # return "soffice"  # works on Windows/Linux if LibreOffice installed


# =====================
# CORE CONVERTER
# =====================
def _convert_to_pdf(input_file: str, output_pdf: str, max_retries=3):
    soffice = get_soffice()
    print("SOFFICE = ", soffice)
    outdir = os.path.dirname(output_pdf)
    print("OUTDIR  = ", outdir)

    for _ in range(max_retries):
        subprocess.run(
            [
                soffice,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to", "pdf",
                "--outdir", outdir,
                input_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        generated_pdf = os.path.join(
            outdir,
            os.path.basename(input_file).rsplit(".", 1)[0] + ".pdf"
        )

        if os.path.exists(generated_pdf):
            os.replace(generated_pdf, output_pdf)
            return

        time.sleep(1)

    raise RuntimeError("LibreOffice PDF conversion failed")


def _convert_to_docx(input_file: str, output_docx: str, max_retries=3):
    soffice = get_soffice()
    outdir = os.path.dirname(output_docx)

    for _ in range(max_retries):
        subprocess.run(
            [
                soffice,
                "--headless",
                "--nologo",
                "--nofirststartwizard",
                "--convert-to", "docx",
                "--outdir", outdir,
                input_file
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        generated_docx = os.path.join(
            outdir,
            os.path.basename(input_file).rsplit(".", 1)[0] + ".docx"
        )

        if os.path.exists(generated_docx):
            os.replace(generated_docx, output_docx)
            return

        time.sleep(1)

    raise RuntimeError("LibreOffice DOCX conversion failed")

def docx_template_to_pdf(file, context: dict) -> str:
    print("CONTEXT = " ,context)
    print("FILE = ",file)
    file.file.seek(0)
    doc = DocxTemplate(BytesIO(file.file.read()))
    doc.render(context)

    pdf_name = f"{uuid.uuid4()}.pdf"
    final_pdf = os.path.join(PDF_DIR, pdf_name)

    print("PDF NAME = ", pdf_name)
    print("FINAL PDF = ", final_pdf)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        doc.save(tmp.name)
        temp_docx = tmp.name

    try:
        _convert_to_pdf(temp_docx, final_pdf)
        return final_pdf
    finally:
        os.unlink(temp_docx)


def html_to_docx(html: str) -> str:
    file_id = str(uuid.uuid4())
    html_path = os.path.join(DOCX_DIR, f"{file_id}.html")
    docx_path = os.path.join(DOCX_DIR, f"{file_id}.docx")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    _convert_to_docx(html_path, docx_path)
    os.unlink(html_path)

    return docx_path


def html_to_pdf(html: str) -> str:
    file_id = str(uuid.uuid4())
    html_path = os.path.join(PDF_DIR, f"{file_id}.html")
    pdf_path = os.path.join(PDF_DIR, f"{file_id}.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    _convert_to_pdf(html_path, pdf_path)
    os.unlink(html_path)

    return pdf_path


def bytes_to_pdf(file_bytes: bytes, suffix=".docx") -> str:
    file_id = str(uuid.uuid4())
    pdf_path = os.path.join(PDF_DIR, f"{file_id}.pdf")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        input_file = tmp.name

    try:
        _convert_to_pdf(input_file, pdf_path)
        return pdf_path
    finally:
        os.unlink(input_file)


def html_to_pdf(html: str) -> str:
    file_id = str(uuid.uuid4())
    html_path = os.path.join(PDF_DIR, f"{file_id}.html")
    pdf_path = os.path.join(PDF_DIR, f"{file_id}.pdf")

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    _convert_to_pdf(html_path, pdf_path)
    os.unlink(html_path)

    return pdf_path


def bytes_to_docx(file_bytes: bytes, suffix=".html") -> str:
    file_id = str(uuid.uuid4())
    docx_path = os.path.join(DOCX_DIR, f"{file_id}.docx")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        input_file = tmp.name

    try:
        _convert_to_docx(input_file, docx_path)
        return docx_path
    finally:
        os.unlink(input_file)
