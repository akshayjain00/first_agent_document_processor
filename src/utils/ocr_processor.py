import pytesseract
from PIL import Image
import logging
from typing import Dict, Optional, List, Tuple
import re
from ..agents.learning_manager import LearningManager

class OCRProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.learning_manager = LearningManager()

    def extract_text(self, image_path: str) -> Dict:
        """
        Extract text from an image using OCR with detailed feedback
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing extracted text, confidence scores, and detailed word data
        """
        try:
            # Open the image
            image = Image.open(image_path)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Process word-level confidence scores and text
            words = []
            total_conf = 0
            valid_word_count = 0
            
            for i in range(len(data['text'])):
                if data['conf'][i] > 0:  # Only consider words with confidence > 0
                    word = data['text'][i].strip()
                    if word:  # Only include non-empty words
                        words.append({
                            'text': word,
                            'confidence': data['conf'][i],
                            'block_num': data['block_num'][i],
                            'line_num': data['line_num'][i],
                            'word_num': data['word_num'][i]
                        })
                        total_conf += data['conf'][i]
                        valid_word_count += 1
            
            # Calculate average confidence
            avg_confidence = total_conf / valid_word_count if valid_word_count > 0 else 0
            
            # Group words by line for better readability
            lines = {}
            for word in words:
                line_key = f"block_{word['block_num']}_line_{word['line_num']}"
                if line_key not in lines:
                    lines[line_key] = []
                lines[line_key].append(word)
            
            # Sort words within each line
            for line in lines.values():
                line.sort(key=lambda x: x['word_num'])
            
            # Extract key fields with their confidences
            fields = self._extract_key_fields(lines)
            
            return {
                "text": pytesseract.image_to_string(image),
                "confidence": avg_confidence,
                "status": "success",
                "details": {
                    "words": words,
                    "lines": lines,
                    "total_words": valid_word_count,
                    "word_confidences": [w['confidence'] for w in words],
                    "fields": fields
                }
            }
            
        except Exception as e:
            self.logger.error(f"OCR extraction failed: {str(e)}")
            return {
                "text": None,
                "confidence": None,
                "status": "error",
                "error": str(e)
            }
    
    def _extract_key_fields(self, lines: Dict) -> Dict[str, Dict[str, float]]:
        """Extract key fields with their confidences"""
        fields = {}
        
        # Common header/boilerplate text to exclude
        HEADER_TEXTS = [
            "UNION OF INDIA",
            "VEHICLES THROUGHOUT INDIA",
            "AUTHORISATION TO DRIVE",
            "FOLLOWING CLASS",
            "STATE MOTOR DRIVING",
            "SIGNATURE",
            "IMPRESSION OF",
            "OLD",
            "NEW",
            "PETH",
            "STAND",
            "DISTRICT",
            "COLONY"
        ]
        
        def is_header_text(text: str) -> bool:
            """Check if text is common header/boilerplate text"""
            return any(header.lower() in text.lower() for header in HEADER_TEXTS)
        
        def find_in_lines(patterns: List[str], preprocess_func=None, min_word_confidence=0, exclude_headers=True, max_words=None, field_name=None) -> Dict[str, float]:
            """Find text matching any of the given patterns with confidence threshold"""
            best_match = {"value": "", "confidence": 0.0}
            best_pattern = None
            for pattern in patterns:
                for line_words in lines.values():
                    # Filter out low confidence words if threshold is set
                    if min_word_confidence > 0:
                        line_words = [w for w in line_words if w["confidence"] >= min_word_confidence]
                    
                    if not line_words:
                        continue
                    
                    # If max_words is set, skip lines that are too long (likely addresses or headers)
                    if max_words and len(line_words) > max_words:
                        continue
                        
                    line_text = " ".join(w["text"] for w in line_words)
                    if exclude_headers and is_header_text(line_text):
                        continue
                        
                    if preprocess_func:
                        line_text = preprocess_func(line_text)
                    
                    matches = re.search(pattern, line_text, re.IGNORECASE)
                    if matches:
                        matched_text = matches.group(1) if len(matches.groups()) > 0 else matches.group(0)
                        matched_text = matched_text.strip()
                        
                        # Skip if the matched text is a header
                        if exclude_headers and is_header_text(matched_text):
                            continue
                        
                        # Skip if the text contains location-specific words
                        if any(word.lower() in matched_text.lower() for word in ["street", "road", "nagar", "colony", "peth", "stand", "district", "dist", "tal"]):
                            continue
                        
                        # Find words that make up the matched text
                        matched_words = []
                        for word in line_words:
                            if (word["text"] in matched_text.split() or 
                                matched_text in word["text"] or 
                                any(part in matched_text for part in word["text"].split())):
                                matched_words.append(word)
                        if matched_words:
                            confidence = sum(w["confidence"] for w in matched_words) / len(matched_words)
                            # Update best match if confidence is higher
                            if confidence > best_match["confidence"]:
                                best_match = {"value": matched_text, "confidence": confidence}
                                best_pattern = pattern
            # Record the successful pattern if found
            if field_name and best_match["value"] and best_pattern:
                self.learning_manager.record_success(field_name, best_pattern)
            return best_match
        
        # License number patterns
        license_patterns = [
            r'(?:DL|License)\s*(?:No\.?|Number:?)[:\s-]*([A-Z0-9\s-]+)(?:\s+DO[!}])?',
            r'(?:MH|KA|DL)\d{2}\s*\d{8,12}',
            r'(?:MH|KA|DL)\d{2}\s*\d{4,8}[A-Z]?',  # Format for some Indian licenses
        ]
        fields["license_number"] = find_in_lines(license_patterns, field_name="license_number")
        
        # Enhanced name detection for driver's licenses
        def clean_name(text):
            """Clean and normalize name text from license"""
            # Remove common prefixes and noise
            text = re.sub(r'^(?:Name\s*[-:.]|\s*Us\s+|\s*S/W\s+of\s+|\s*[SW]/[ODW]\s+)', '', text, flags=re.IGNORECASE)
            # Remove text after common separators
            text = re.sub(r'\s+(?:S/O|D/O|W/O|S/|D/|W/|of|SO|DO|WO)\s+.*$', '', text, flags=re.IGNORECASE)
            # Remove common metadata markers
            text = re.sub(r'\s*(?:DOB|BG|ADD?|PIN|Age).*$', '', text, flags=re.IGNORECASE)
            # Remove location-specific words
            text = re.sub(r'\s*(?:STREET|ROAD|NAGAR|COLONY|PETH|STAND|DISTRICT|DIST|TAL|VILLAGE|VLG).*$', '', text, flags=re.IGNORECASE)
            return text.strip()

        # Enhanced name patterns for Indian driver's licenses
        name_patterns = [
            # Primary name patterns with known prefixes
            r'(?:Name\s*[-:.]|\bUs\b|\bS/W\s+of\b)\s*[-:]?\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)',
            
            # Name with relation prefix patterns
            r'(?:^|\s)([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)\s*(?:S/O|D/O|W/O|S/|D/|W/|of|SO|DO|WO)',
            
            # Strict all-caps name pattern (2-3 words)
            r'\b([A-Z]+\s+[A-Z]+(?:\s+[A-Z]+)?)\b(?:\s*(?:S/O|D/O|W/O|of))?',
            
            # Mixed case name pattern
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b',
            
            # Name after common Indian prefixes
            r'(?:Sri|Shri|Smt|Mr|Mrs|Ms)\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)+)',
        ]
        
        # Use stricter parameters for name detection
        name_result = find_in_lines(
            patterns=name_patterns,
            preprocess_func=clean_name,
            min_word_confidence=75.0,  # Slightly lower threshold to catch more candidates
            max_words=4,  # Names typically won't be more than 4 words
            exclude_headers=True,
            field_name="name"
        )

        # Post-process name to ensure proper capitalization
        if name_result["value"]:
            # Properly capitalize each part of the name
            name_parts = name_result["value"].split()
            name_result["value"] = " ".join(part.title() for part in name_parts)

        fields["name"] = name_result
        
        # Expiry date patterns
        date_patterns = [
            r'Valid\s+Till[.:\s;]*(\d{2}[-/]\d{2}[-/]\d{4})',
            r'Valid\s+Until[.:\s;]*(\d{2}[-/]\d{2}[-/]\d{4})',
            r'Expiry[.:\s;]*(\d{2}[-/]\d{2}[-/]\d{4})',
        ]
        fields["expiry_date"] = find_in_lines(date_patterns, field_name="expiry_date")
        
        # License class patterns
        def clean_class(text):
            # Remove noise and standardize format
            text = text.upper().strip()
            text = re.sub(r'[^A-Z0-9\s]', '', text)
            return text
        
        # Specific patterns for Indian driving license classes
        class_patterns = [
            r'\b(?:MCWG|LMV|MC|TRANS)\b',  # Common Indian license classes
            r'(?:Class|COV)[.:\s]*([A-Z]+(?:\s*[A-Z0-9]*)*)',
            r'\b(?:MCWG|LMV)[-\s]*(?:\d{2}[-/]\d{2}[-/]\d{4})?',  # Class with optional date
        ]
        
        # Get all potential classes
        class_result = find_in_lines(class_patterns, clean_class, min_word_confidence=70.0, exclude_headers=False, field_name="license_class")
        
        # Clean up the class result
        if class_result["value"]:
            # Extract just the class part if there's a date
            class_match = re.match(r'^(MCWG|LMV|MC|TRANS)', class_result["value"])
            if class_match:
                class_result["value"] = class_match.group(1)
        
        fields["license_class"] = class_result
        
        return fields