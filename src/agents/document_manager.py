from typing import Dict, List
import logging
from .license_verifier import LicenseVerifier

class DocumentManagerAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.license_verifier = LicenseVerifier()
    
    def process_document(self, document_path: str, document_type: str) -> Dict:
        """
        Process a new document and coordinate verification
        
        Args:
            document_path: Path to the uploaded document
            document_type: Type of document (license, id, registration, etc.)
            
        Returns:
            Dict containing verification results
        """
        try:
            # Phase 1: Only handling driver's license
            if document_type.lower() != "driver_license":
                return {"status": "rejected", "reason": "Currently only processing driver's licenses"}
                
            # Delegate to license verification agent
            verification_result = self.license_verifier.verify_license(document_path)
            
            # Log the verification attempt
            self.logger.info(f"Processed document {document_path} with result: {verification_result}")
            
            return verification_result
            
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            return {"status": "error", "reason": str(e)}