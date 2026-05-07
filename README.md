#  AI Document OCR & NLP Pipeline

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Claude AI](https://img.shields.io/badge/Claude_AI-Anthropic-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=for-the-badge&logo=streamlit)
![Tesseract OCR](https://img.shields.io/badge/Tesseract-OCR-yellow?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

**Production-grade AI pipeline for extracting structured data from invoices, receipts, contracts, and scanned PDFs using OCR + LLM.**

[ Live Demo](#-quick-start) · [ API Docs](#-api-endpoints) · [ Hire Me on Upwork](https://www.upwork.com/freelancers/~0120e5107410edbd72?mp_source=share)

</div>

---

##  What This Project Does

This pipeline automatically converts **unstructured documents** (PDFs, scanned images, photos) into **clean, structured JSON data** using:

- **Tesseract OCR** for text extraction from images and scanned PDFs
- **pdfplumber** for native PDF text extraction
- **Claude AI (Anthropic)** for intelligent NLP-based data structuring
- **FastAPI** for production REST API
- **Streamlit** for a zero-code web interface

**Real business impact:** Eliminates 90%+ of manual data entry from documents. Used in production for finance, logistics, healthcare, and legal industries.

---

##  Key Features

| Feature | Description |
|---|---|
|  **Multi-format OCR** | PDF, PNG, JPG, TIFF, BMP support |
|  **AI-Powered Extraction** | Claude LLM understands context, not just regex patterns |
|  **Auto Document Detection** | Automatically classifies invoices, receipts, contracts |
|  **Structured JSON Output** | Clean, normalized data ready for databases/ERP/APIs |
|  **FastAPI REST API** | Production-ready endpoints with Swagger docs |
|  **Streamlit UI** | No-code drag-and-drop web interface |
|  **Docker Ready** | One-command deployment anywhere |
|  **Batch Processing** | Process entire folders of documents at once |



##  Architecture

```
Document (PDF/Image)
        │
        ▼
┌─────────────────────┐
│   Input Handler     │  ← Validates format, routes to correct extractor
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   OCR Engine        │  ← Tesseract OCR (images) + pdfplumber (PDFs)
│   (Text Extraction) │     Auto-fallback: if PDF has no text → OCR
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   Document          │  ← Detects: invoice / receipt / contract / general
│   Classifier        │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   Claude AI NLP     │  ← Type-specific structured extraction prompt
│   (Data Extractor)  │     Returns normalized JSON
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│   JSON Output       │  ← Clean structured data saved to file
└─────────────────────┘
```

---

## Quick Start

### Option 1 — Docker (Recommended)

```bash
git clone https://github.com/Sherazkarim1/ai-document-ocr-nlp-pipeline.git
cd ai-document-ocr-nlp-pipeline
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
docker-compose up --build
```

- **API**: http://localhost:8000/docs
- **UI**: http://localhost:8501

### Option 2 — Local Setup

```bash
# Clone the repo
git clone https://github.com/Sherazkarim1/ai-document-ocr-nlp-pipeline.git
cd ai-document-ocr-nlp-pipeline

# Install Tesseract OCR
# macOS:  brew install tesseract
# Ubuntu: sudo apt install tesseract-ocr
# Windows: https://github.com/UB-Mannheim/tesseract/wiki

# Install Python dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add ANTHROPIC_API_KEY to .env

# Run API
uvicorn src.api:app --reload --port 8000

# Run UI (separate terminal)
streamlit run src/app.py
```

---

##  Python SDK Usage

### Single Document

```python
from src.ocr_pipeline import DocumentOCRPipeline

pipeline = DocumentOCRPipeline()

# Auto-detect document type
result = pipeline.process("invoice.pdf")

# Force document type
result = pipeline.process("scan.jpg", doc_type="invoice")

print(result["extracted_data"])
# {
#   "invoice_number": "INV-2024-847",
#   "vendor_name": "TechSolutions Inc.",
#   "total_amount": 13188.80,
#   "line_items": [...],
#   ...
# }
```

### Batch Processing

```python
from src.ocr_pipeline import batch_process

results = batch_process("./invoices_folder/", doc_type="invoice")
# Processes all PDFs and images in folder
# Saves individual JSON files to outputs/
```

---

##  API Endpoints

Start the API: `uvicorn src.api:app --reload`
Swagger Docs: `http://localhost:8000/docs`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Service info |
| `GET` | `/health` | Health check |
| `POST` | `/process` | Upload & process single document |
| `GET` | `/result/{job_id}` | Retrieve extraction result |
| `GET` | `/supported-formats` | List supported file types |

### Example API Call

```bash
curl -X POST http://localhost:8000/process \
  -F "file=@invoice.pdf" \
  -F "doc_type=invoice"
```

**Response:**
```json
{
  "job_id": "a3f8c1d2",
  "status": "completed",
  "data": {
    "document_type": "invoice",
    "extracted_data": {
      "invoice_number": "INV-2024-847",
      "vendor_name": "TechSolutions Inc.",
      "total_amount": 13188.80,
      "line_items": [
        {"description": "AI Integration Consulting", "quantity": 40, "unit_price": 150, "total": 6000}
      ]
    }
  }
}
```

---

## Output Format Examples

### Invoice Extraction
```json
{
  "invoice_number": "INV-2024-847",
  "date": "2024-01-15",
  "due_date": "2024-02-15",
  "vendor_name": "TechSolutions Inc.",
  "client_name": "Acme Corporation",
  "line_items": [
    {"description": "AI Integration Consulting", "quantity": 40, "unit_price": 150.00, "total": 6000.00}
  ],
  "subtotal": 12800.00,
  "tax": 1028.80,
  "discount": 640.00,
  "total_amount": 13188.80,
  "currency": "USD",
  "payment_terms": "Net 30"
}
```

### Receipt Extraction
```json
{
  "store_name": "Whole Foods Market",
  "date": "2024-03-10",
  "items": [
    {"name": "Organic Milk", "quantity": 1, "price": 5.99}
  ],
  "subtotal": 45.20,
  "tax": 3.85,
  "total": 49.05,
  "payment_method": "VISA *4521"
}
```

---

##  Project Structure

```
ai-document-ocr-nlp-pipeline/
├── src/
│   ├── ocr_pipeline.py      # Core OCR + AI extraction engine
│   ├── api.py               # FastAPI REST API
│   └── app.py               # Streamlit web UI
├── data/
│   └── sample_invoices/     # Sample documents for testing
├── tests/
│   └── test_pipeline.py     # Unit tests
├── outputs/                 # Extracted JSON results
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

##  Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| OCR Engine | Tesseract 5.x | Image/scanned PDF text extraction |
| PDF Parsing | pdfplumber | Native PDF text extraction |
| AI NLP | Claude (Anthropic) | Intelligent structured data extraction |
| REST API | FastAPI | Production API with auto-docs |
| Web UI | Streamlit | No-code drag-and-drop interface |
| Containerization | Docker + Compose | One-command deployment |
| Testing | pytest | Unit & integration tests |



##  Keywords & Use Cases

> **OCR invoice extraction** · **PDF data extraction Python** · **AI document processing** · **NLP invoice parser** · **receipt OCR Python** · **contract data extraction** · **document AI pipeline** · **LLM document understanding** · **Tesseract OCR FastAPI** · **invoice automation Python** · **structured data extraction PDF** · **AI-powered OCR pipeline** · **document digitization AI** · **intelligent document processing IDP**

**Industries served:** Finance & Accounting · Legal & Compliance · Healthcare · Logistics & Supply Chain · Real Estate · E-Commerce



##  Customization

Add a new document type in 3 steps:

```python
# 1. Add extraction prompt in ocr_pipeline.py
EXTRACTION_PROMPTS["bank_statement"] = """Extract all bank statement data..."""

# 2. Update detect_document_type()
if any(k in text_lower for k in ["account statement", "opening balance"]):
    return "bank_statement"

# 3. Done! The pipeline automatically uses your new type
result = pipeline.process("statement.pdf", doc_type="bank_statement")
```

---

##  Running Tests

```bash
pip install pytest
pytest tests/ -v
```

##  License

MIT License — free to use, modify, and distribute.


##  About the Author

**Sheraz Karim** — Top Rated AI Developer on Upwork with expertise in:
-  Generative AI & LLM Applications
-  RAG Pipelines & Vector Databases
-  OCR & Document Intelligence
-  AI Workflow Automation (n8n, Zapier)
-  Cloud Deployment (AWS, Azure, GCP)

 **[Hire me on Upwork](https://www.upwork.com/freelancers/~0120e5107410edbd72?mp_source=share)** for your next AI project.


<div align="center">

 **Star this repo if it helped you!** 

</div>
