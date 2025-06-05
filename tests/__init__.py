"""Testing package initialisation."""

# Provide lightweight stubs for optional external dependencies so that
# the unit tests can run in minimal environments where packages like
# Pillow or pytesseract may not be installed.
import sys
import types

if 'pytesseract' not in sys.modules:
    pytesseract = types.ModuleType('pytesseract')
    pytesseract.image_to_string = lambda *args, **kwargs: ''
    pytesseract.image_to_data = lambda *args, **kwargs: {
        'text': [],
        'conf': [],
        'block_num': [],
        'line_num': [],
        'word_num': []
    }
    sys.modules['pytesseract'] = pytesseract

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
