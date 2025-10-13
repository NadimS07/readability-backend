from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import textstat

app = FastAPI()

# ✅ Enable CORS so frontend can talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Readability API is running"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_text(request: Request):
    data = await request.json()
    text = data.get("text", "")
    if not text:
        return {"error": "No text provided"}

    results = {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "gunning_fog_index": textstat.gunning_fog(text),
        "smog_index": textstat.smog_index(text),
        "automated_readability_index": textstat.automated_readability_index(text),
        "coleman_liau_index": textstat.coleman_liau_index(text),
        "linsear_write_formula": textstat.linsear_write_formula(text),
        "dale_chall_score": textstat.dale_chall_readability_score(text),
    }

    return results
