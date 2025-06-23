from typing import List, Dict

def format_suggestions(suggestions: List[str]) -> List[Dict]:
    """format thhe sugesstion into a structured response"""
    return [
        {
            "id": i + 1,
            "suggestion": suggestion,
            "confidence": round((1 - (0.1 * i)), 2)
        }
        for i, suggestion in enumerate(suggestions)
    ]