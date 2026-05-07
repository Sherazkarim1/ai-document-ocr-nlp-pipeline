"""
AI-Powered Document OCR & NLP Pipeline
Extracts structured data from invoices, receipts, contracts, and PDFs
Author: Sheraz Karim | Upwork Top Rated AI Developer
"""

import os
import json
import re
from pathlib import Path
from typing import Optional
import pytesseract
from PIL import Image
import pdfplumber
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class DocumentOCRPipeline:
    """
    End-to-end OCR + NLP pipeline for structured data extraction
    Supports: Invoices, Receipts, Contracts, Medical Records, Bank Statements
    """

    SUPPORTED_FORMATS = [".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]

    EXTRACTION_PROMPTS = {
        "invoice": """Extract all invoice data and return ONLY valid JSON:
{
  "invoice_number": "",
  "date": "",
  "due_date": "",
  "vendor_name": "",
  "vendor_address": "",
  "client_name": "",
  "client_address": "",
  "line_items": [{"description": "", "quantity": 0, "unit_price": 0, "total": 0}],
  "subtotal": 0,
  "tax": 0,
  "discount": 0,
  "total_amount": 0,
  "currency": "",
  "payment_terms": "",
  "bank_details": {}
}""",
        "receipt": """Extract all receipt data and return ONLY valid JSON:
{
  "store_name": "",
  "date": "",
  "time": "",
  "receipt_number": "",
  "items": [{"name": "", "quantity": 0, "price": 0}],
  "subtotal": 0,
  "tax": 0,
  "total": 0,
  "payment_method": "",
  "cashier": ""
}""",
        "contract": """Extract key contract data and return ONLY valid JSON:
{
  "contract_title": "",
  "parties": [],
  "effective_date": "",
  "expiry_date": "",
  "contract_value": "",
  "key_obligations": [],
  "payment_terms": "",
  "termination_clause": "",
  "governing_law": ""
}""",
        "general": """Extract all key information from this document and return ONLY valid JSON with relevant fields."""
    }

    def __init__(self):
        self.extracted_text = ""
        self.document_type = "general"

    def load_document(self, file_path: str) -> str:
        """Load document and extract raw text via OCR or PDF parsing."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {suffix}. Supported: {self.SUPPORTED_FORMATS}")

        print(f"📄 Loading document: {path.name}")

        if suffix == ".pdf":
            return self._extract_from_pdf(file_path)
        else:
            return self._extract_from_image(file_path)

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {i+1} ---\n{page_text}"
                else:
                    # Fallback to OCR for scanned pages
                    image = page.to_image(resolution=300)
                    ocr_text = pytesseract.image_to_string(image.original)
                    text += f"\n--- Page {i+1} (OCR) ---\n{ocr_text}"
        return text.strip()

    def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using Tesseract OCR."""
        image = Image.open(file_path)
        # Preprocess: convert to grayscale for better accuracy
        image = image.convert("L")
        text = pytesseract.image_to_string(image, config="--psm 6")
        return text.strip()

    def detect_document_type(self, text: str) -> str:
        """Auto-detect document type from content."""
        text_lower = text.lower()
        if any(k in text_lower for k in ["invoice", "bill to", "invoice number", "inv-"]):
            return "invoice"
        elif any(k in text_lower for k in ["receipt", "thank you for your purchase", "pos"]):
            return "receipt"
        elif any(k in text_lower for k in ["agreement", "contract", "terms and conditions", "whereas"]):
            return "contract"
        return "general"

    def extract_structured_data(self, raw_text: str, doc_type: Optional[str] = None) -> dict:
        """Use Claude AI to extract structured data from raw OCR text."""
        if not doc_type:
            doc_type = self.detect_document_type(raw_text)

        print(f"🤖 Detected document type: {doc_type}")
        print("🧠 Running AI extraction with Claude...")

        prompt = self.EXTRACTION_PROMPTS.get(doc_type, self.EXTRACTION_PROMPTS["general"])

        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2000,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\nDocument text:\n{raw_text}"
                }
            ]
        )

        response_text = message.content[0].text.strip()
        # Clean up markdown code blocks if present
        response_text = re.sub(r"```json\n?", "", response_text)
        response_text = re.sub(r"```\n?", "", response_text)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return {"raw_extraction": response_text, "parse_error": True}

    def process(self, file_path: str, doc_type: Optional[str] = None, save_output: bool = True) -> dict:
        """Full pipeline: load → OCR → NLP → structured JSON output."""
        # Step 1: Extract raw text
        raw_text = self.load_document(file_path)
        self.extracted_text = raw_text

        # Step 2: AI-powered structured extraction
        structured_data = self.extract_structured_data(raw_text, doc_type)

        # Step 3: Save results
        result = {
            "source_file": str(file_path),
            "document_type": doc_type or self.detect_document_type(raw_text),
            "raw_text_length": len(raw_text),
            "extracted_data": structured_data
        }

        if save_output:
            output_path = Path("outputs") / f"{Path(file_path).stem}_extracted.json"
            output_path.parent.mkdir(exist_ok=True)
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            print(f"✅ Saved to: {output_path}")

        return result


def batch_process(folder_path: str, doc_type: Optional[str] = None) -> list:
    """Process all documents in a folder."""
    pipeline = DocumentOCRPipeline()
    results = []
    folder = Path(folder_path)

    files = [f for f in folder.iterdir() if f.suffix.lower() in DocumentOCRPipeline.SUPPORTED_FORMATS]
    print(f"📂 Found {len(files)} documents to process")

    for file in files:
        print(f"\n🔄 Processing: {file.name}")
        result = pipeline.process(str(file), doc_type)
        results.append(result)
        print(f"✅ Done: {file.name}")

    print(f"\n🎉 Batch complete! Processed {len(results)} documents")
    return results


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = DocumentOCRPipeline().process(sys.argv[1])
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python ocr_pipeline.py <path_to_document>")
