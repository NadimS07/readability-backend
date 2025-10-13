from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import textstat
import requests
from transformers import pipeline

app = FastAPI(title="WriteWise Backend", version="2.0")

# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend URL later for security
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tone Analyzer (HuggingFace model)
sentiment_pipeline = pipeline("sentiment-analysis")

@app.get("/")
def root():
    return {"message": "WriteWise Backend is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze_readability")
async def analyze_readability(request: Request):
    data = await request.json()
    text = data.get("text", "")

    scores = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "gunning_fog_index": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "dale_chall_score": textstat.dale_chall_readability_score(text),
    }

    summary = {
        "overall_readability": (
            "Very Easy" if scores["flesch_reading_ease"] > 80 else
            "Moderate" if scores["flesch_reading_ease"] > 50 else
            "Very Difficult"
        ),
        "education_level": (
            "Elementary School" if scores["gunning_fog_index"] < 6 else
            "High School" if scores["gunning_fog_index"] < 12 else
            "College / Research"
        ),
        "sentence_complexity": (
            "Simple" if scores["smog_index"] < 8 else
            "Moderate" if scores["smog_index"] < 12 else
            "Very Complex"
        ),
        "word_simplicity": (
            "Basic Vocabulary" if scores["dale_chall_score"] < 5 else
            "Advanced Vocabulary"
        ),
        "insight": "Your text has been evaluated for readability and linguistic difficulty.",
        "suggestion": "Try shorter sentences and simpler vocabulary for better clarity.",
    }

    return {"summary": summary, "raw_scores": scores}


@app.post("/analyze_grammar")
async def analyze_grammar(request: Request):
    data = await request.json()
    text = data.get("text", "")

    response = requests.post(
        "https://api.languagetool.org/v2/check",
        data={"text": text, "language": "en-US"},
    )

    if response.status_code != 200:
        return {"error": "Grammar check failed"}

    grammar_data = response.json()
    issues = [
        {"message": m["message"], "context": m["context"]["text"]}
        for m in grammar_data.get("matches", [])
    ]

    return {"grammar_issues": issues, "total_issues": len(issues)}


@app.post("/analyze_tone")
async def analyze_tone(request: Request):
    data = await request.json()
    text = data.get("text", "")

    result = sentiment_pipeline(text[:500])[0]
    tone = result["label"]
    confidence = round(result["score"] * 100, 2)

    tone_description = {
        "POSITIVE": "Optimistic or encouraging tone.",
        "NEGATIVE": "Critical or pessimistic tone.",
        "NEUTRAL": "Objective and factual tone."
    }.get(tone.upper(), "Mixed tone detected.")

    return {
        "tone": tone.capitalize(),
        "confidence": f"{confidence}%",
        "description": tone_description
    }