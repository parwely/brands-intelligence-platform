# backend/app/ml/preprocessing/text_cleaner.py
import re
import string
from typing import List, Optional, Dict
import nltk
from textblob import TextBlob
import logging

logger = logging.getLogger(__name__)

# Download required NLTK data (run once)
def setup_nltk():
    """Download NLTK data if not present"""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        logger.info("Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("NLTK data downloaded successfully")

# Initialize NLTK
setup_nltk()

class TextPreprocessor:
    """Advanced text preprocessing for sentiment analysis"""
    
    def __init__(self):
        try:
            from nltk.corpus import stopwords
            self.stop_words = set(stopwords.words('english'))
        except Exception as e:
            logger.warning(f"Could not load stopwords: {e}")
            self.stop_words = set()
    
    def clean_text(self, text: str) -> str:
        """Basic text cleaning"""
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags (but keep the content)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#(\w+)', r'\1', text)  # Keep hashtag content
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def advanced_clean(self, text: str) -> str:
        """Advanced cleaning with tokenization"""
        text = self.clean_text(text)
        
        # Remove punctuation but keep emoticons
        emoticons = re.findall(r'[😀-🙏🌀-🗿🚀-🛿☀-⛿]', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize and remove stopwords
        try:
            tokens = nltk.word_tokenize(text)
            tokens = [token for token in tokens if token.lower() not in self.stop_words and len(token) > 2]
            # Add back emoticons
            tokens.extend(emoticons)
            return ' '.join(tokens)
        except Exception as e:
            logger.warning(f"Tokenization failed: {e}")
            return text
    
    def extract_features(self, text: str) -> Dict:
        """Extract comprehensive text features for analysis"""
        if not text:
            return self._empty_features()
        
        try:
            blob = TextBlob(text)
            cleaned = self.clean_text(text)
            advanced_cleaned = self.advanced_clean(text)
            
            # Count features
            word_count = len(text.split())
            char_count = len(text)
            sentence_count = len(blob.sentences)
            
            # Sentiment features
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Text pattern features
            has_exclamation = '!' in text
            has_question = '?' in text
            has_caps = any(c.isupper() for c in text)
            caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
            
            # Emotional indicators
            has_emoji = bool(re.search(r'[😀-🙏🌀-🗿🚀-🛿☀-⛿]', text))
            exclamation_count = text.count('!')
            question_count = text.count('?')
            
            return {
                'word_count': word_count,
                'char_count': char_count,
                'sentence_count': sentence_count,
                'polarity': round(polarity, 3),
                'subjectivity': round(subjectivity, 3),
                'has_exclamation': has_exclamation,
                'has_question': has_question,
                'has_caps': has_caps,
                'caps_ratio': round(caps_ratio, 3),
                'has_emoji': has_emoji,
                'exclamation_count': exclamation_count,
                'question_count': question_count,
                'cleaned_text': cleaned,
                'advanced_cleaned': advanced_cleaned,
                'avg_word_length': round(sum(len(word) for word in text.split()) / word_count, 2) if word_count > 0 else 0
            }
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return self._empty_features()
    
    def _empty_features(self) -> Dict:
        """Return empty features dict"""
        return {
            'word_count': 0, 'char_count': 0, 'sentence_count': 0,
            'polarity': 0.0, 'subjectivity': 0.0, 'has_exclamation': False,
            'has_question': False, 'has_caps': False, 'caps_ratio': 0.0,
            'has_emoji': False, 'exclamation_count': 0, 'question_count': 0,
            'cleaned_text': '', 'advanced_cleaned': '', 'avg_word_length': 0.0
        }

# Test the preprocessor
if __name__ == "__main__":
    preprocessor = TextPreprocessor()
    
    sample_texts = [
        "OMG! This brand is AMAZING!!! Love their service 😍 #BestBrand https://example.com",
        "Terrible experience. Worst product I've ever bought. Never again!",
        "The product is okay. Nothing special, but does the job."
    ]
    
    print("🔧 Testing Text Preprocessor...")
    print("=" * 50)
    
    for i, text in enumerate(sample_texts, 1):
        print(f"\n{i}. Original: {text}")
        features = preprocessor.extract_features(text)
        print(f"   Cleaned: {features['cleaned_text']}")
        print(f"   Advanced: {features['advanced_cleaned']}")
        print(f"   Features: Words={features['word_count']}, Sentiment={features['polarity']:.2f}, Caps={features['has_caps']}")