from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import textstat
from textblob import TextBlob
import difflib
import logging

# -------------------------------------------------------------------
# 🚀 Initialize FastAPI App
# -------------------------------------------------------------------
app = FastAPI(
    title="Readability, Tone & Plagiarism Analyzer API",
    version="3.3.0",
    description="AI-powered readability, tone, and plagiarism analysis for English text.",
)

# -------------------------------------------------------------------
# 🧾 Enable Logging (for Railway Logs)
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# 🌐 Enable CORS (for Vercel + Local + Debug)
# -------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # temporarily open for full access
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
def health_check():
    logger.info("Health check accessed ✅")
    return {"status": "ok"}

# -------------------------------------------------------------------
# 📘 1️⃣ Readability Analyzer
# -------------------------------------------------------------------
@app.post("/analyze_readability")
def analyze_readability(data: InputText, request: Request):
    logger.info(f"📘 Readability request from {request.client.host}")
    text = data.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}

    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "gunning_fog_index": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "dale_chall_score": textstat.dale_chall_readability_score(text),
    }

    avg = (scores["flesch_reading_ease"] + 206 - scores["gunning_fog_index"]) / 2

    summary = {
        "overall_readability": (
            "Very Difficult" if avg < 30 else "Moderate" if avg < 70 else "Easy"
        ),
        "education_level": (
            "Graduate / Research" if avg < 30 else "College" if avg < 70 else "High School"
        ),
        "sentence_complexity": (
            "Very Complex" if scores["gunning_fog_index"] > 18 else "Moderate"
        ),
        "word_simplicity": (
            "Advanced Vocabulary" if scores["dale_chall_score"] > 9 else "Moderate Vocabulary"
        ),
        "insight": (
            "Your text is highly complex and challenging for general readers."
            if avg < 30
            else "Your text is moderately readable and accessible to most readers."
            if avg < 70
            else "Your text is clear and easy to understand."
        ),
        "suggestion": (
            "Break long sentences and use simpler words for better comprehension."
            if avg < 30
            else "Keep your sentences concise and well-balanced."
            if avg < 70
            else "Excellent readability! Maintain this clarity in your writing."
        ),
    }

    return {"summary": summary, "raw_scores": scores}

# -------------------------------------------------------------------
# 💬 2️⃣ Tone Analyzer
# -------------------------------------------------------------------
@app.post("/analyze_tone")
def analyze_tone(data: InputText, request: Request):
    logger.info(f"💬 Tone request from {request.client.host}")
    text = data.text.strip()
    if not text:
        return {"error": "Text cannot be empty."}

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
        "Highly Positive": "Your tone feels enthusiastic, confident, and optimistic.",
        "Slightly Positive": "Your tone sounds warm and engaging.",
        "Neutral": "Your tone is balanced, factual, and professional.",
        "Slightly Negative": "Your tone feels cautious or mildly critical.",
        "Highly Negative": "Your tone sounds strongly emotional or critical. Try softening phrases for balance.",
    }

    summary = {
        "dominant_tone": tone,
        "confidence": f"{abs(polarity) * 100:.1f}%",
        "feedback": feedback_map[tone],
    }

    return {"summary": summary, "tone_value": polarity}

# -------------------------------------------------------------------
# 🔍 3️⃣ Simple Plagiarism Checker
# -------------------------------------------------------------------
@app.post("/check_plagiarism")
def check_plagiarism(data: InputText, request: Request):
    logger.info(f"🔍 Plagiarism request from {request.client.host}")
    text = data.text.strip()
    if not text:
        logger.warning("⚠️ Empty text received in plagiarism endpoint.")
        return {"error": "Text cannot be empty."}

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

    logger.info(f"✅ Plagiarism analysis complete with score: {plagiarism_score}%")
    return {"summary": summary, "similarity_reference": plagiarism_score}

# -------------------------------------------------------------------
# 🌍 Root Route
# -------------------------------------------------------------------
@app.get("/")
def root():
    logger.info("Root route accessed 🌍")
    return {"message": "Readability, Tone & Plagiarism Analyzer API is running successfully!"}
