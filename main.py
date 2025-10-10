from fastapi import FastAPI
from pydantic import BaseModel
import textstat
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Root endpoint
@app.get("/")
def root():
    return {"message": "Backend is live!"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextInput(BaseModel):
    text: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/score")
def score(input: TextInput):
    text = input.text
    return {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "gunning_fog_index": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
    }
