from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import uuid
import json
from typing import Optional

from .db import get_db_connection
from .services.orchestrator import orchestrator
from .src.agents.prompt_architect import PromptArchitectAgent

app = FastAPI()
prompt_architect = PromptArchitectAgent()

# ... (CORS middleware remains same)

class FrameInvestigationRequest(BaseModel):
    raw_input: str

@app.post("/api/frame-investigation")
def frame_investigation(req: FrameInvestigationRequest):
    expanded_prompt = prompt_architect.generate_prompt(req.raw_input)
    return {"generated_prompt": expanded_prompt}

# ... (Rest of existing login logic)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

class AnalyzeRequest(BaseModel):
    raw_input: str
    user_id: int 
    original_input: Optional[str] = None # The user's raw idea, if different from framed prompt

@app.post("/api/login")
def login(req: LoginRequest):
    # Hardcoded v1 auth
    if req.username == "demo" and req.password == "demo123":
        return {"status": "ok", "user_id": 1, "username": "demo"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/analyze")
def start_analysis(req: AnalyzeRequest, background_tasks: BackgroundTasks):
    analysis_id = str(uuid.uuid4())
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO analyses (id, user_id, raw_input, original_input, status) VALUES (?, ?, ?, ?, ?)",
        (analysis_id, req.user_id, req.raw_input, req.original_input, "QUEUED")
    )
    conn.commit()
    conn.close()
    
    # Trigger Orchestrator
    background_tasks.add_task(orchestrator.run_analysis, analysis_id, req.user_id, req.raw_input, req.original_input)
    
    return {"analysis_id": analysis_id, "status": "QUEUED"}

@app.get("/api/status/{analysis_id}")
def get_status(analysis_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    row = cursor.execute("SELECT status, verdict, confidence FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Analysis not found")

    status_raw = row['status']
    
    # Define stage order
    STAGES = [
        "VERIFYING",
        "HUNTING",
        "MINING",
        "SYNTHESIZING",
        "JUSTIFYING",
        "KILL_SWITCH",
        "ARCHITECTING",
        "COMPLETED"
    ]

    completed_stages = []
    current_stage = status_raw

    # Handle completion states
    if "COMPLETED" in status_raw:
        completed_stages = STAGES[:-1] 
        current_stage = "COMPLETED"
    elif "FAILED" in status_raw:
        current_stage = "FAILED"
    else:
        try:
            # Find index
            idx = STAGES.index(status_raw)
            completed_stages = STAGES[:idx]
        except ValueError:
            # excessive safety
            completed_stages = []

    return {
        "analysis_id": analysis_id,
        "current_stage": current_stage,
        "completed_stages": completed_stages,
        "verdict": row['verdict']
    }

@app.get("/api/report/{analysis_id}")
def get_report(analysis_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch core
    analysis = cursor.execute("SELECT * FROM analyses WHERE id = ?", (analysis_id,)).fetchone()
    if not analysis:
        conn.close()
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # Fetch details
    evidence = cursor.execute("SELECT * FROM evidence_signals WHERE analysis_id = ?", (analysis_id,)).fetchall()
    clusters = cursor.execute("SELECT * FROM pain_clusters WHERE analysis_id = ?", (analysis_id,)).fetchall()
    features = cursor.execute("SELECT * FROM feature_decisions WHERE analysis_id = ?", (analysis_id,)).fetchall()
    kill_switch = cursor.execute("SELECT * FROM kill_switch WHERE analysis_id = ?", (analysis_id,)).fetchone()
    prd_row = cursor.execute("SELECT * FROM prd WHERE analysis_id = ?", (analysis_id,)).fetchone()
    
    conn.close()
    
    analysis_dict = dict(analysis)
    if analysis_dict.get('confidence_metadata'):
        try:
            analysis_dict['confidence_metadata'] = json.loads(analysis_dict['confidence_metadata'])
        except:
            pass

    return {
        "analysis": analysis_dict,
        "evidence": [dict(r) for r in evidence],
        "clusters": [dict(r) for r in clusters],
        "feature_decisions": [dict(r) for r in features],
        "kill_switch": dict(kill_switch) if kill_switch else None,
        "prd": json.loads(prd_row['content_json']) if prd_row and prd_row['content_json'] else None
    }

@app.get("/api/analyses")
def list_analyses(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT id, raw_input, status, verdict, created_at FROM analyses WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
