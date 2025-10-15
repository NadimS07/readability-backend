from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import textstat
from textblob import TextBlob
import difflib
import logging

# -------------------------------------------------------------------
# 🚀 Initialize App
# -------------------------------------------------------------------
app = FastAPI(
    title="Readability, Tone & Plagiarism Analyzer API",
    version="3.5.0",
    description="AI-powered readability, tone, and plagiarism analysis for English text.",
)

# -------------------------------------------------------------------
# 🧾 Logging Setup
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("analyzer")

# -------------------------------------------------------------------
# 🌐 CORS Configuration
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ Keep open during testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# 📦 Input Schema
# -------------------------------------------------------------------
class InputText(BaseModel):
    text: str

# -------------------------------------------------------------------
# 🩺 Health Check
# -------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------------------------
# 📘 Readability Analyzer
# -------------------------------------------------------------------
@app.post("/analyze_readability")
def analyze_readability(data: InputText):
    text = data.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}
    
    logger.info("📘 Readability endpoint hit")

    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "gunning_fog_index": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "dale_chall_score": textstat.dale_chall_readability_score(text),
    }

    avg = (scores["flesch_reading_ease"] + 206 - scores["gunning_fog_index"]) / 2

    summary = {
        "overall_readability": "Very Difficult" if avg < 30 else "Moderate" if avg < 70 else "Easy",
        "education_level": "Graduate / Research" if avg < 30 else "College" if avg < 70 else "High School",
        "sentence_complexity": "Very Complex" if scores["gunning_fog_index"] > 18 else "Moderate",
        "word_simplicity": "Advanced Vocabulary" if scores["dale_chall_score"] > 9 else "Moderate Vocabulary",
        "insight": "Highly complex text." if avg < 30 else "Moderately readable." if avg < 70 else "Clear and easy to read.",
        "suggestion": "Simplify structure and vocabulary." if avg < 30 else "Good balance." if avg < 70 else "Excellent readability.",
    }

    return {"summary": summary, "raw_scores": scores}

# -------------------------------------------------------------------
# 💬 Tone Analyzer
# -------------------------------------------------------------------
@app.post("/analyze_tone")
def analyze_tone(data: InputText):
    text = data.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}
    
    logger.info("💬 Tone endpoint hit")

    blob = TextBlob(text)
    polarity = blob.sentiment.polarity

    if polarity > 0.6:
        tone = "Highly Positive"
    elif polarity > 0.2:
        tone = "Slightly Positive"
    elif polarity > -0.2:
        tone = "Neutral"
    elif polarity > -0.6:
        tone = "Slightly Negative"
    else:
        tone = "Highly Negative"

    feedback_map = {
        "Highly Positive": "Your tone feels enthusiastic and optimistic.",
        "Slightly Positive": "Your tone sounds warm and encouraging.",
        "Neutral": "Your tone is balanced and factual.",
        "Slightly Negative": "Your tone feels cautious or mildly critical.",
        "Highly Negative": "Your tone sounds emotional or strongly critical.",
    }

    return {
        "summary": {
            "dominant_tone": tone,
            "confidence": f"{abs(polarity) * 100:.1f}%",
            "feedback": feedback_map[tone],
        },
        "tone_value": polarity,
    }

# -------------------------------------------------------------------
# 🔍 Plagiarism Checker
# -------------------------------------------------------------------
@app.post("/check_plagiarism")
def check_plagiarism(data: InputText, request: Request):
    text = data.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}
    
    logger.info(f"🔍 Plagiarism endpoint hit from {request.client.host}")

    reference_texts = [
        "Artificial intelligence is transforming how people work, learn, and communicate.",
        "The quick brown fox jumps over the lazy dog.",
        "Machine learning enables systems to learn automatically from data without being explicitly programmed.",
        "FastAPI is a modern web framework for building APIs with Python.",
    ]

    max_similarity = 0
    for ref in reference_texts:
        similarity = difflib.SequenceMatcher(None, text.lower(), ref.lower()).ratio()
        max_similarity = max(max_similarity, similarity)

    plagiarism_score = round(max_similarity * 100, 2)

    summary = {
        "plagiarism_score": f"{plagiarism_score}%",
        "feedback": (
            "⚠️ High similarity detected. Consider rephrasing or citing sources."
            if plagiarism_score > 60
            else "✅ No significant plagiarism detected. Your content appears original."
        ),
    }

    logger.info(f"✅ Plagiarism Score: {plagiarism_score}%")
    return {"summary": summary, "similarity_reference": plagiarism_score}

# -------------------------------------------------------------------
# 🧠 OPTIONS handler for preflight (fixes browser block)
# -------------------------------------------------------------------
@app.options("/{rest_of_path:path}")
def preflight_handler(rest_of_path: str):
    logger.info(f"🕊️ CORS preflight for path: /{rest_of_path}")
    return {"status": "CORS preflight OK"}

# -------------------------------------------------------------------
# 🌍 Root Route
# -------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "Readability, Tone & Plagiarism Analyzer API is running successfully!"}
