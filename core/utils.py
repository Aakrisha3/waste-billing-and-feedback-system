# core/utils.py
from textblob import TextBlob

def analyze_feedback(feedback_text: str) -> str:
    if not feedback_text:
        return "Neutral"
    polarity = TextBlob(feedback_text).sentiment.polarity
    if polarity > 0.05:
        return "Positive"
    elif polarity < -0.05:
        return "Negative"
    return "Neutral"

