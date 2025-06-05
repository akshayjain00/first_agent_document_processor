# AI Agent-based Driver Documentation Processing

A Python-based system for automated processing and verification of driver documentation using AI agents and OCR.

## Phase 1 Features
- Driver's license document processing and verification
- OCR-based text extraction
- Basic information validation (expiry dates, license numbers, etc.)
- Human review workflow integration

## Requirements
- Python 3.9+
- Tesseract OCR
- Dependencies listed in requirements.txt

## Setup
1. Install Tesseract OCR:
   ```bash
   # For macOS
   brew install tesseract
   # For Ubuntu/Debian
   # sudo apt-get install tesseract-ocr
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the OpenAI API key for the optional swarm orchestrator:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   ```
   The key can also be placed in a `.env` file based on `example.env`.

## Project Structure
- `src/agents/`: Contains the agent implementations
  - `document_manager.py`: Main document processing coordinator
  - `license_verifier.py`: Specialized agent for license verification
- `src/utils/`: Utility modules
  - `ocr_processor.py`: OCR processing utilities
- `tests/`: Unit tests

## Running Tests
```bash
python -m unittest discover tests
```

## Usage Example
```python
from src.agents.document_manager import DocumentManagerAgent

# Initialize the document manager
manager = DocumentManagerAgent()

# Process a driver's license
result = manager.process_document(
    document_path="path/to/license.jpg",
    document_type="driver_license"
)

print(result)  # Shows verification status and extracted information
```