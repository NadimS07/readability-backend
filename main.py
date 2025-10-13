from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import textstat

app = FastAPI()

# Enable CORS for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict to your frontend domain
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

    # Get original readability metrics
    flesch = textstat.flesch_reading_ease(text)
    fog = textstat.gunning_fog(text)
    smog = textstat.smog_index(text)
    ari = textstat.automated_readability_index(text)
    dale = textstat.dale_chall_readability_score(text)

    # Derived values
    avg_grade = (fog + smog + ari) / 3

    # Interpretations
    if flesch >= 80:
        readability = "Very Easy"
    elif flesch >= 60:
        readability = "Easy"
    elif flesch >= 40:
        readability = "Moderate"
    elif flesch >= 20:
        readability = "Difficult"
    else:
        readability = "Very Difficult"

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

    if fog > 18 or smog > 14:
        sentence_complexity = "Very Complex"
    elif fog > 14:
        sentence_complexity = "Moderate"
    else:
        sentence_complexity = "Simple"

    if dale > 10:
        word_simplicity = "Advanced Vocabulary"
    elif dale > 8:
        word_simplicity = "Moderate Vocabulary"
    else:
        word_simplicity = "Simple Vocabulary"

    return {
        "summary": {
            "overall_readability": readability,
            "education_level": level,
            "sentence_complexity": sentence_complexity,
            "word_simplicity": word_simplicity,
        },
        "raw_scores": {
            "flesch_reading_ease": flesch,
            "gunning_fog_index": fog,
            "smog_index": smog,
            "automated_readability_index": ari,
            "dale_chall_score": dale,
        },
    }