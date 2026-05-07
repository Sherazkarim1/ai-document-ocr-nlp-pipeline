"""
Unit tests for AI Document OCR & NLP Pipeline
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.ocr_pipeline import DocumentOCRPipeline


@pytest.fixture
def pipeline():
    return DocumentOCRPipeline()


def test_supported_formats(pipeline):
    assert ".pdf" in pipeline.SUPPORTED_FORMATS
    assert ".png" in pipeline.SUPPORTED_FORMATS
    assert ".jpg" in pipeline.SUPPORTED_FORMATS


def test_unsupported_format_raises(pipeline):
    with pytest.raises(ValueError, match="Unsupported format"):
        pipeline.load_document("document.xyz")


def test_detect_invoice_type(pipeline):
    text = "Invoice Number: INV-001\nBill To: John Smith\nTotal Amount: $500"
    assert pipeline.detect_document_type(text) == "invoice"


def test_detect_receipt_type(pipeline):
    text = "Receipt #12345\nThank you for your purchase\nTotal: $45.00"
    assert pipeline.detect_document_type(text) == "receipt"


def test_detect_contract_type(pipeline):
    text = "This Agreement is entered into\nWhereas the parties agree\nTermination clause"
    assert pipeline.detect_document_type(text) == "contract"


def test_detect_general_type(pipeline):
    text = "Some random document content here"
    assert pipeline.detect_document_type(text) == "general"


def test_extraction_prompts_exist(pipeline):
    assert "invoice" in pipeline.EXTRACTION_PROMPTS
    assert "receipt" in pipeline.EXTRACTION_PROMPTS
    assert "contract" in pipeline.EXTRACTION_PROMPTS
    assert "general" in pipeline.EXTRACTION_PROMPTS


@patch("src.ocr_pipeline.client")
def test_extract_structured_data(mock_client, pipeline):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text='{"invoice_number": "INV-001", "total_amount": 500}')]
    mock_client.messages.create.return_value = mock_response

    result = pipeline.extract_structured_data(
        "Invoice Number: INV-001 Total: $500",
        doc_type="invoice"
    )
    assert result.get("invoice_number") == "INV-001"
    assert result.get("total_amount") == 500


def test_batch_process_empty_folder(tmp_path):
    from src.ocr_pipeline import batch_process
    results = batch_process(str(tmp_path))
    assert results == []
