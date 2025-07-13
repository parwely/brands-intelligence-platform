# Simple TextPreprocessor
from typing import Dict

class TextPreprocessor:
    def __init__(self):
        pass

    async def extract_features(self, text: str) -> Dict:
        return {
            'char_count': len(text),
            'word_count': len(text.split()),
            'sentence_count': 1
        }
