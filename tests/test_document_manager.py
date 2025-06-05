import unittest
from unittest.mock import MagicMock, patch
import sys
import types

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

from src.agents.document_manager import DocumentManagerAgent


class TestDocumentManagerAgent(unittest.TestCase):
    @patch('src.agents.document_manager.SwarmOrchestrator')
    def test_process_document_uses_swarm(self, mock_orchestrator_cls):
        orchestrator = MagicMock()
        orchestrator.run_license_verifier.return_value = {'status': 'pending_review'}
        mock_orchestrator_cls.return_value = orchestrator

        agent = DocumentManagerAgent()
        result = agent.process_document('dummy.jpg', 'driver_license')

        self.assertEqual(result['status'], 'pending_review')
        orchestrator.run_license_verifier.assert_called_with('dummy.jpg')

