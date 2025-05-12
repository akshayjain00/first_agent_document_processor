import os
import sys
from pathlib import Path
import statistics

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.append(str(src_path))

from src.agents.document_manager import DocumentManagerAgent
from src.utils.ocr_processor import OCRProcessor
from datetime import datetime


def setup_test_environment():
    """Setup directories for testing"""
    base_dir = "test_docs"
    upload_dir = os.path.join(base_dir, "uploads")
    processed_dir = os.path.join(base_dir, "processed")
    
    # Create directories if they don't exist
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)
    
    return upload_dir, processed_dir

def analyze_ocr_results(document_path: str):
    """Analyze OCR results in detail"""
    ocr = OCRProcessor()
    result = ocr.extract_text(document_path)
    
    if result["status"] != "success":
        print(f"Error: {result.get('error', 'Unknown error')}")
        return
    
    print("\nDetailed OCR Analysis")
    print("=" * 50)
    
    # Overall statistics
    confidences = result["details"]["word_confidences"]
    if confidences:
        print(f"\nConfidence Statistics:")
        print(f"Average Confidence: {statistics.mean(confidences):.2f}%")
        print(f"Median Confidence: {statistics.median(confidences):.2f}%")
        print(f"Min Confidence: {min(confidences):.2f}%")
        print(f"Max Confidence: {max(confidences):.2f}%")
        print(f"Total Words Detected: {result['details']['total_words']}")
    
    # Print recognized text by line with confidence scores
    print("\nRecognized Text by Line:")
    print("-" * 50)
    for line_key, line_words in result["details"]["lines"].items():
        print(f"\nLine {line_key}:")
        line_text = " ".join(word["text"] for word in line_words)
        line_conf = statistics.mean(word["confidence"] for word in line_words)
        print(f"Text: {line_text}")
        print(f"Confidence: {line_conf:.2f}%")
        
        # Show individual word confidences
        print("Word confidences:")
        for word in line_words:
            print(f"  '{word['text']}': {word['confidence']:.2f}%")
    
    return result

def process_test_document(document_path: str, document_type: str):
    """Process a single document and print results"""
    print(f"\nProcessing document: {document_path}")
    print("-" * 50)
    
    # First get detailed OCR analysis
    ocr_result = analyze_ocr_results(document_path)
    
    # Then process through document manager
    manager = DocumentManagerAgent()
    result = manager.process_document(document_path, document_type)
    
    print("\nDocument Manager Processing Result:")
    print(f"Status: {result['status']}")
    print(f"Reason: {result.get('reason', 'N/A')}")
    
    if 'extracted_info' in result:
        print("\nExtracted Information:")
        for key, value in result['extracted_info'].items():
            print(f"{key}: {value}")
    
    print("\nOverall Confidence Score:", result.get('confidence', 'N/A'))
    print("-" * 50)
    
    return result

def main():
    upload_dir, processed_dir = setup_test_environment()
    
    print("Document Processing System Test")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Process a new document")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "2":
            break
        elif choice == "1":
            document_path = input("\nEnter the path to your document (or drag & drop): ").strip()
            # Remove quotes if present (from drag & drop)
            document_path = document_path.strip("'\"")
            
            if not os.path.exists(document_path):
                print("Error: Document not found!")
                continue
                
            document_type = input("Enter document type (driver_license): ").strip()
            if not document_type:
                document_type = "driver_license"  # default for testing
            
            process_test_document(document_path, document_type)

if __name__ == "__main__":
    main()