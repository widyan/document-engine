from fastapi import FastAPI, UploadFile, File, Body, HTTPException
from fastapi.responses import FileResponse
from app.services.document_service import (
    docx_template_to_pdf,
    html_to_docx,
    html_to_pdf,
    bytes_to_pdf,
    bytes_to_docx
)
import json


app = FastAPI(title="Document Engine Service")


@app.post("/docx/template-to-pdf")
async def api_docx_template_to_pdf(
    file: UploadFile = File(...),
    context: str = Body(...)
):
    try:
        data = json.loads(context)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Context must be valid JSON")
    print("CONTEXT PAYLOAD = ", context)
    print("CONTEXT PAYLOAD JSON = ", data)
    path = docx_template_to_pdf(file, data)
    return {"status": "success", "path": path}


@app.post("/html/to-docx")
async def api_html_to_docx(html: str = Body(...)):
    path = html_to_docx(html)
    return {"status": "success", "path": path}


@app.post("/html/to-pdf")
async def api_html_to_pdf(html: str = Body(...)):
    path = html_to_pdf(html)
    return {"status": "success", "path": path}


@app.post("/bytes/to-pdf")
async def api_bytes_to_pdf(file: UploadFile = File(...)):
    content = await file.read()
    path = bytes_to_pdf(content, suffix=".docx")
    return {"status": "success", "path": path}


@app.post("/bytes/to-docx")
async def api_bytes_to_docx(file: UploadFile = File(...)):
    content = await file.read()
    path = bytes_to_docx(content, suffix=".html")
    return {"status": "success", "path": path}


@app.get("/download")
def download(path: str):
    return FileResponse(path, filename=path.split("\\")[-1])
