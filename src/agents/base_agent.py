import logging
from typing import Dict, Any, List
from .learning_manager import LearningManager

class BaseAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.memory: List[Dict[str, Any]] = []  # Store context/history
        self.learning_stats: Dict[str, int] = {}  # Track successful document types
        self.learning_manager = LearningManager()

    def _make_decision(self, document_data: Dict[str, Any]) -> str:
        """
        Decide what to do with the document based on learning stats.
        Returns:
            str: 'auto_approve' if seen before, else 'flag_for_review'
        """
        doc_type = document_data.get("type", "unknown")
        if self.learning_stats.get(doc_type, 0) > 1:
            return "auto_approve"
        else:
            return "flag_for_review"

    def process_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the document data and store context in memory.
        Args:
            document_data (Dict[str, Any]): Data and metadata for the document to be processed.
        Returns:
            Dict[str, Any]: Processing result including status and any extracted info.
        """
        try:
            self.logger.info("Starting document processing.")
            self.memory.append(document_data)
            doc_type = document_data.get("type", "unknown")
            # Update learning stats
            self.learning_stats[doc_type] = self.learning_stats.get(doc_type, 0) + 1
            decision = self._make_decision(document_data)
            result = {
                "status": "success",
                "decision": decision,
                "message": f"Decision: {decision}",
                "document_data": document_data,
                "learning_stats": self.learning_stats
            }
            self.logger.info("Document processing completed.")
            return result
        except Exception as e:
            self.logger.error(f"Error processing document: {str(e)}")
            return {"status": "error", "reason": str(e)}

    def feedback(self, field: str, pattern: str, correct: bool):
        """
        Provide feedback on a pattern for a field (positive or negative).
        """
        self.learning_manager.record_feedback(field, pattern, correct)
        self.logger.info(f"Feedback recorded for field '{field}', pattern '{pattern}', correct={correct}")

if __name__ == "__main__":
    import json
    logging.basicConfig(level=logging.INFO)
    agent = BaseAgent()
    test_document = {
        "id": "doc_001",
        "type": "driver_license",
        "path": "/path/to/sample/license.jpg"
    }
    result = agent.process_document(test_document)
    print(json.dumps(result, indent=2))
