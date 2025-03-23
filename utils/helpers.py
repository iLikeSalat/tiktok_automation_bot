import os
import json
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}

def save_json(data, file_path):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")
        return False

def extract_keywords(text, max_keywords=5):
    text = re.sub(r'[^\w\s]', '', text.lower())
    words = text.split()
    stopwords = ["the", "and", "is", "in", "to", "a", "for", "of", "with", "that", "this"]
    keywords = [word for word in words if word not in stopwords and len(word) > 3]
    return list(set(keywords))[:max_keywords]
