from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import textstat

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace * with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "Readability API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze_text(req: TextRequest):
    text = req.text

    # Calculate readability metrics
    flesch = textstat.flesch_reading_ease(text)
    fog = textstat.gunning_fog(text)
    smog = textstat.smog_index(text)
    ari = textstat.automated_readability_index(text)
    dale = textstat.dale_chall_readability_score(text)

    # Average readability score
    avg_grade = (fog + smog + ari) / 3

    # 1️⃣ Overall readability
    if flesch >= 80:
        readability = "Very Easy"
        insight = "Your writing is highly accessible — perfect for all audiences."
        suggestion = "Consider adding variety or complexity if writing for professionals."
    elif flesch >= 60:
        readability = "Easy"
        insight = "Your text is clear and easy to read for most people."
        suggestion = "You're doing great — keep sentences concise and engaging."
    elif flesch >= 40:
        readability = "Moderate"
        insight = "Your writing is moderately complex — suitable for mature readers."
        suggestion = "Simplify long sentences and replace advanced words where possible."
    elif flesch >= 20:
        readability = "Difficult"
        insight = "Your text is quite complex — suitable for professional or academic readers."
        suggestion = "Use shorter sentences and simpler vocabulary to enhance clarity."
    else:
        readability = "Very Difficult"
        insight = "Your text is highly complex and challenging for general readers."
        suggestion = "Break long sentences and use everyday words to improve readability."

    # 2️⃣ Education level
    if avg_grade <= 6:
        level = "Elementary School"
    elif avg_grade <= 9:
        level = "Middle School"
    elif avg_grade <= 12:
        level = "High School"
    elif avg_grade <= 16:
        level = "College Level"
    else:
        level = "Graduate / Research"

    # 3️⃣ Sentence complexity
    if fog > 18 or smog > 14:
        sentence_complexity = "Very Complex"
    elif fog > 14:
        sentence_complexity = "Moderate"
    else:
        sentence_complexity = "Simple"

    # 4️⃣ Word simplicity
    if dale > 10:
        word_simplicity = "Advanced Vocabulary"
    elif dale > 8:
        word_simplicity = "Moderate Vocabulary"
    else:
        word_simplicity = "Simple Vocabulary"

    # Return structured JSON
    return {
        "summary": {
            "overall_readability": readability,
            "education_level": level,
            "sentence_complexity": sentence_complexity,
            "word_simplicity": word_simplicity,
            "insight": insight,
            "suggestion": suggestion
        },
        "raw_scores": {
            "flesch_reading_ease": flesch,
            "gunning_fog_index": fog,
            "smog_index": smog,
            "automated_readability_index": ari,
            "dale_chall_score": dale,
        },
    }