import unittest
from unittest.mock import Mock, patch
import os
import shutil
from datetime import datetime, timedelta
import sys
import types

# Provide stubs for optional dependencies
if 'pytesseract' not in sys.modules:
    t = types.ModuleType('pytesseract')
    t.image_to_string = lambda *a, **k: ''
    t.image_to_data = lambda *a, **k: {'text': [], 'conf': [], 'block_num': [], 'line_num': [], 'word_num': []}
    sys.modules['pytesseract'] = t
if 'PIL' not in sys.modules:
    pil = types.ModuleType('PIL')
    class Image:
        @staticmethod
        def open(path):
            return None
    pil.Image = Image
    pil.ImageDraw = types.SimpleNamespace()
    pil.ImageFont = types.SimpleNamespace()
    sys.modules['PIL'] = pil
if 'dotenv' not in sys.modules:
    dotenv = types.ModuleType('dotenv')
    dotenv.load_dotenv = lambda *a, **k: None
    sys.modules['dotenv'] = dotenv

from src.agents.license_verifier import LicenseVerifier
from src.config.settings import Settings
from test_data import TestDataGenerator

class TestLicenseVerifier(unittest.TestCase):
    def setUp(self):
        self.verifier = LicenseVerifier()
        self.test_data_dir = "test_data"
        self.data_generator = TestDataGenerator(self.test_data_dir)
        
    def tearDown(self):
        # Clean up test data directory
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
    
    @patch('src.utils.ocr_processor.OCRProcessor.extract_text')
    def test_valid_license_processing(self, mock_extract):
        # Mock OCR response with valid data
        mock_extract.return_value = {
            "text": "NAME: John Smith\nLICENSE: A1234567\nCLASS: C\nEXPIRY: 31-12-2026",
            "confidence": 95.5,
            "status": "success",
            "details": {
                "fields": {
                    "name": {"value": "John Smith", "confidence": 95.5},
                    "license_number": {"value": "A1234567", "confidence": 95.5},
                    "license_class": {"value": "C", "confidence": 95.5},
                    "expiry_date": {"value": "31-12-2026", "confidence": 95.5}
                }
            }
        }
        
        result = self.verifier.verify_license("dummy_path.jpg")
        
        self.assertEqual(result["status"], "pending_review")
        self.assertTrue(result["needs_human_review"])
        self.assertEqual(result["extracted_info"]["name"], "John Smith")
        self.assertEqual(result["extracted_info"]["license_number"], "A1234567")
        self.assertEqual(result["extracted_info"]["expiry_date"], "31-12-2026")
        self.assertEqual(result["extracted_info"]["license_class"], "C")
        
    @patch('src.utils.ocr_processor.OCRProcessor.extract_text')
    def test_expired_license(self, mock_extract):
        past_date = (datetime.now() - timedelta(days=30)).strftime("%d-%m-%Y")
        mock_extract.return_value = {
            "text": f"NAME: John Smith\nLICENSE: A1234567\nCLASS: C\nEXPIRY: {past_date}",
            "confidence": 95.5,
            "status": "success",
            "details": {
                "fields": {
                    "name": {"value": "John Smith", "confidence": 95.5},
                    "license_number": {"value": "A1234567", "confidence": 95.5},
                    "license_class": {"value": "C", "confidence": 95.5},
                    "expiry_date": {"value": past_date, "confidence": 95.5}
                }
            }
        }
        
        result = self.verifier.verify_license("dummy_path.jpg")
        
        self.assertEqual(result["status"], "rejected")
        self.assertIn("expired", result["reason"].lower())
        
    @patch('src.utils.ocr_processor.OCRProcessor.extract_text')
    def test_invalid_license_class(self, mock_extract):
        mock_extract.return_value = {
            "text": "NAME: John Smith\nLICENSE: A1234567\nCLASS: X\nEXPIRY: 31-12-2026",
            "confidence": 95.5,
            "status": "success",
            "details": {
                "fields": {
                    "name": {"value": "John Smith", "confidence": 95.5},
                    "license_number": {"value": "A1234567", "confidence": 95.5},
                    "license_class": {"value": "X", "confidence": 95.5},
                    "expiry_date": {"value": "31-12-2026", "confidence": 95.5}
                }
            }
        }
        
        result = self.verifier.verify_license("dummy_path.jpg")
        
        self.assertEqual(result["status"], "rejected")
        self.assertIn("not acceptable", result["reason"].lower())
        
    @patch('src.utils.ocr_processor.OCRProcessor.extract_text')
    def test_low_confidence_rejection(self, mock_extract):
        mock_extract.return_value = {
            "text": "NAME: John Smith\nLICENSE: A1234567\nCLASS: C\nEXPIRY: 31-12-2026",
            "confidence": Settings.OCR_CONFIDENCE_THRESHOLD - 10,
            "status": "success",
            "details": {
                "fields": {
                    "name": {"value": "John Smith", "confidence": 95.5},
                    "license_number": {"value": "A1234567", "confidence": 95.5},
                    "license_class": {"value": "C", "confidence": 95.5},
                    "expiry_date": {"value": "31-12-2026", "confidence": 95.5}
                }
            }
        }
        
        result = self.verifier.verify_license("dummy_path.jpg")
        
        self.assertEqual(result["status"], "rejected")
        self.assertTrue(result.get("needs_better_image", False))
        self.assertIn("confidence", result["reason"].lower())
        
    @patch('src.utils.ocr_processor.OCRProcessor.extract_text')
    def test_missing_required_fields(self, mock_extract):
        mock_extract.return_value = {
            "text": "LICENSE: A1234567\nCLASS: C\nEXPIRY: 31-12-2026",  # Missing name
            "confidence": 95.5,
            "status": "success",
            "details": {
                "fields": {
                    "license_number": {"value": "A1234567", "confidence": 95.5},
                    "license_class": {"value": "C", "confidence": 95.5},
                    "expiry_date": {"value": "31-12-2026", "confidence": 95.5}
                }
            }
        }
        
        result = self.verifier.verify_license("dummy_path.jpg")
        
        self.assertEqual(result["status"], "rejected")
        self.assertIn("required fields", result["reason"].lower())
        self.assertIn("name", result["reason"].lower())