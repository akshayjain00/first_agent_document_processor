from datetime import datetime
from typing import Dict, Optional
from ..utils.ocr_processor import OCRProcessor
from ..config.settings import Settings
import re
import logging

class LicenseVerifier:
    def __init__(self):
        self.ocr = OCRProcessor()
        self.logger = logging.getLogger(__name__)
        self.requirements = Settings.get_license_requirements()

    def verify_license(self, document_path: str) -> Dict:
        """
        Verify a driver's license document
        
        Args:
            document_path: Path to the license document
            
        Returns:
            Dict containing verification results
        """
        # Extract text from license
        ocr_result = self.ocr.extract_text(document_path)
        
        if ocr_result["status"] != "success":
            return {
                "status": "rejected",
                "reason": "Failed to extract text from document",
                "error": ocr_result.get("error")
            }

        # Get field-specific results
        field_results = ocr_result["details"]["fields"]
        
        # Extract and validate information
        extracted_info = {}
        failed_fields = []
        low_confidence_fields = []

        # Check each required field
        for field in self.requirements["required_fields"]:
            if field not in field_results or not field_results[field]["value"]:
                failed_fields.append(field)
            elif field_results[field]["confidence"] < self.requirements["field_confidence_thresholds"][field]:
                low_confidence_fields.append(f"{field} ({field_results[field]['confidence']:.1f}%)")
            
            extracted_info[field] = field_results[field]["value"]

        # Add license class if found
        if "license_class" in field_results and field_results["license_class"]["value"]:
            extracted_info["license_class"] = field_results["license_class"]["value"]

        # Check for failures
        if failed_fields:
            return {
                "status": "rejected",
                "reason": f"Could not extract required fields: {', '.join(failed_fields)}",
                "extracted_info": extracted_info
            }

        if low_confidence_fields:
            return {
                "status": "rejected",
                "reason": f"Low confidence in fields: {', '.join(low_confidence_fields)}",
                "extracted_info": extracted_info,
                "needs_better_image": True
            }

        # Validate the extracted information
        validation_result = self._validate_license_info(extracted_info)
        if validation_result["status"] == "rejected":
            return {**validation_result, "extracted_info": extracted_info}

        return {
            "status": "pending_review",
            "needs_human_review": True,
            "reason": "Valid information extracted, awaiting human verification",
            "extracted_info": extracted_info,
            "confidence": ocr_result["confidence"]
        }

    def _validate_license_info(self, info: Dict[str, str]) -> Dict:
        """Validate the extracted license information"""
        # Check expiration
        try:
            expiry_date = datetime.strptime(info["expiry_date"], "%d-%m-%Y")
            if expiry_date < datetime.now():
                return {
                    "status": "rejected",
                    "reason": "License is expired"
                }
        except ValueError:
            return {
                "status": "rejected",
                "reason": "Invalid expiry date format"
            }

        # Validate license class if present
        if "license_class" in info and info["license_class"]:
            if info["license_class"] not in self.requirements["acceptable_classes"]:
                return {
                    "status": "rejected",
                    "reason": f"License class {info['license_class']} not acceptable for ride sharing"
                }

        return {"status": "success"}