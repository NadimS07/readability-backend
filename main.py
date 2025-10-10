from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import textstat

app = FastAPI(title="Readability API", version="1.0")

# -----------------------------
# Pydantic model for request
# -----------------------------
class TextRequest(BaseModel):
    text: str

# -----------------------------
# Root endpoint
# -----------------------------
@app.get("/")
async def root():
    return {"message": "Readability API is running"}

# -----------------------------
# Health endpoint
# -----------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}

# -----------------------------
# Readability endpoint
# -----------------------------
@app.post("/analyze")
async def analyze_text(request: TextRequest):
    try:
        text = request.text
        if not text:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        readability = {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "smog_index": textstat.smog_index(text),
            "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
            "coleman_liau_index": textstat.coleman_liau_index(text),
            "automated_readability_index": textstat.automated_readability_index(text),
            "dale_chall_readability_score": textstat.dale_chall_readability_score(text),
            "difficult_words": textstat.difficult_words(text),
            "linsear_write_formula": textstat.linsear_write_formula(text),
            "gunning_fog": textstat.gunning_fog(text),
            "text_standard": textstat.text_standard(text)
        }

        return {"readability": readability}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
