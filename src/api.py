"""
FastAPI REST API for Document OCR & NLP Pipeline
Endpoints for uploading, processing, and retrieving extracted document data
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import uuid
import json
from pathlib import Path
from typing import Optional
from src.ocr_pipeline import DocumentOCRPipeline

app = FastAPI(
    title="AI Document OCR & NLP API",
    description="Extract structured data from invoices, receipts, contracts using AI-powered OCR",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

job_status = {}


@app.get("/")
def root():
    return {
        "service": "AI Document OCR & NLP Pipeline",
        "version": "1.0.0",
        "endpoints": ["/process", "/batch-process", "/result/{job_id}", "/health"]
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ocr-nlp-pipeline"}


@app.post("/process")
async def process_document(
    file: UploadFile = File(...),
    doc_type: Optional[str] = None
):
    """
    Upload and process a single document.
    Supported: PDF, PNG, JPG, JPEG, TIFF
    doc_type options: invoice, receipt, contract, general (auto-detected if not provided)
    """
    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {allowed_extensions}"
        )

    job_id = str(uuid.uuid4())[:8]
    save_path = UPLOAD_DIR / f"{job_id}_{file.filename}"

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        pipeline = DocumentOCRPipeline()
        result = pipeline.process(str(save_path), doc_type)
        job_status[job_id] = {"status": "completed", "result": result}
        return JSONResponse(content={"job_id": job_id, "status": "completed", "data": result})
    except Exception as e:
        job_status[job_id] = {"status": "failed", "error": str(e)}
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        save_path.unlink(missing_ok=True)


@app.get("/result/{job_id}")
def get_result(job_id: str):
    """Retrieve the result of a previously processed document."""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status[job_id]


@app.get("/supported-formats")
def get_supported_formats():
    """List all supported document formats and extraction types."""
    return {
        "formats": [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"],
        "document_types": ["invoice", "receipt", "contract", "general"],
        "output_format": "JSON"
    }
