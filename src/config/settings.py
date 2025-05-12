from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # OCR Configuration
    OCR_CONFIDENCE_THRESHOLD = float(os.getenv('OCR_CONFIDENCE_THRESHOLD', '85.0'))
    
    # Field-specific confidence thresholds
    FIELD_CONFIDENCE_THRESHOLDS = {
        'license_number': 70.0,  # Lowered due to complex format with spaces and special chars
        'name': 75.0,           # Name threshold
        'expiry_date': 75.0,    # Expiry date threshold
        'license_class': 75.0   # License class threshold
    }
    
    # Document Verification Settings
    REQUIRED_LICENSE_FIELDS = ['license_number', 'expiry_date', 'name']
    LICENSE_CLASS_REQUIREMENTS = {
        'ride_sharing': ['A', 'B', 'C', 'LMV', 'MCWG']  # Added more valid classes
    }
    
    # Processing Paths
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
    PROCESSED_DIR = os.getenv('PROCESSED_DIR', 'processed')
    
    @classmethod
    def get_license_requirements(cls) -> Dict:
        """Get license verification requirements"""
        return {
            'required_fields': cls.REQUIRED_LICENSE_FIELDS,
            'acceptable_classes': cls.LICENSE_CLASS_REQUIREMENTS['ride_sharing'],
            'min_confidence': cls.OCR_CONFIDENCE_THRESHOLD,
            'field_confidence_thresholds': cls.FIELD_CONFIDENCE_THRESHOLDS
        }