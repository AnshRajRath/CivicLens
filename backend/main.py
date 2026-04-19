import time
import uuid
import logging
import sys
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from typing import List, Optional, Dict

# FIX: Add current directory to path so imports work from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.civic_brain import run_analysis_pipeline
except ImportError:
    from civic_brain import run_analysis_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CivicLens")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisResponse(BaseModel):
    thread_id: str
    feasibility_score: int
    trust_score: int
    summary: str
    chart_image: Optional[str] = None
    processing_time: float

class QuizSubmission(BaseModel):
    answers: Dict[str, int]

class QuizResult(BaseModel):
    match_percentage: int
    aligned_party: str
    explanation: str
    quadrant_x: float
    quadrant_y: float

def parse_pdf(file_file) -> str:
    try:
        reader = PdfReader(file_file)
        text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t: text += t
        return text if text.strip() else "Fallback: Promise to reduce taxes."
    except Exception:
        return "Error reading PDF."

@app.get("/health")
def health_check():
    return {"status": "active"}

@app.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_document(file: UploadFile = File(...)):
    logger.info(f"Receiving file: {file.filename}")
    thread_id = str(uuid.uuid4())
    text = parse_pdf(file.file)
    start = time.time()
    
    try:
        result = run_analysis_pipeline(thread_id, text)
        duration = time.time() - start
        
        # Calculate scores
        score = result.get("quality_score", 50)
        trust = 90
        for h in result.get("historical_context", []):
            if "Broken" in h: trust -= 20

        return {
            "thread_id": thread_id,
            "feasibility_score": score,
            "trust_score": trust,
            "summary": str(result.get("final_report", "Analysis Failed")),
            "chart_image": result.get("chart_base64", None),
            "processing_time": duration
        }
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/quiz-alignment", response_model=QuizResult)
async def calculate_alignment(submission: QuizSubmission):
    score_econ = sum(val for q, val in submission.answers.items() if int(q) % 2 != 0)
    score_social = sum(val for q, val in submission.answers.items() if int(q) % 2 == 0)
    
    x = (score_econ / 15) * 10
    y = (score_social / 10) * 10
    
    party = "Centrist"
    if x > 3: party = "Liberty Party"
    if x < -3: party = "Social Union"
    
    return {
        "match_percentage": 88,
        "aligned_party": party,
        "explanation": f"Based on your score, you align with {party}.",
        "quadrant_x": x,
        "quadrant_y": y
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)