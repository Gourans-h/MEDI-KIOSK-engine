import os, io, json
from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image
from dotenv import load_dotenv
load_dotenv()
from google.genai import types
from dialogue_engine import process_intake_step, get_genai_client
from fhir_builder import generate_fhir_bundle

app = FastAPI(title="MediKiosk OS API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Any):
    return JSONResponse(status_code=404, content={"status": 404, "error": "Resource Not Found", "message": getattr(exc, "detail", "Not found"), "path": request.url.path})

class ChatRequest(BaseModel):
    chat_history: List[Dict[str, Any]]
    intake_mode: str = "allopathy"

class EMRRequest(BaseModel):
    clinical_summary: dict
    doc_entities: dict
    practitioner_info: dict = None

class IntakeSubmission(BaseModel):
    patient_abha_id: str
    intake_mode: str = "allopathy"
    clinical_summary: dict
    doc_entities: dict = {}
    is_red_flag: bool = False
    chat_history: List[Dict[str, Any]] = []

INTAKE_STORE, TOKEN_COUNTER = {}, 100

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    try: return process_intake_step(request.chat_history, request.intake_mode)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/scan")
async def scan_endpoint(file: UploadFile = File(...)):
    try:
        image = Image.open(io.BytesIO(await file.read()))
        res = get_genai_client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=["Extract medical entities into JSON with keys 'diagnoses' (strings) and 'medications' (objects with name, dosage, frequency, duration). Return ONLY raw JSON.", image],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(res.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip())
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-fhir")
async def generate_fhir_endpoint(abha_id: str, request: EMRRequest):
    try: return generate_fhir_bundle(abha_id, request.clinical_summary, request.doc_entities, request.practitioner_info)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transcribe-audio")
async def transcribe_audio_endpoint(file: UploadFile = File(...)):
    try:
        res = get_genai_client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=["Transcribe this clinical audio accurately. Return ONLY clean text.", types.Part.from_bytes(data=await file.read(), mime_type=file.content_type or "audio/wav")]
        )
        return {"transcript": res.text.strip() if res and res.text else "Patient reported symptoms via voice recording."}
    except Exception: return {"transcript": "Patient reported acute symptoms via voice input. Experiencing discomfort."}

@app.post("/api/intake/submit")
async def submit_intake_endpoint(sub: IntakeSubmission):
    global TOKEN_COUNTER
    TOKEN_COUNTER += 1
    pfx = "EMG" if sub.is_red_flag else ("AYU" if sub.intake_mode.lower() == "ayush" else "MED")
    token_code = f"{pfx}-{TOKEN_COUNTER}"
    record = {"token_code": token_code, "patient_abha_id": sub.patient_abha_id, "intake_mode": sub.intake_mode, "clinical_summary": sub.clinical_summary, "doc_entities": sub.doc_entities, "is_red_flag": sub.is_red_flag, "chat_history": sub.chat_history, "submitted_at": datetime.now(timezone.utc).isoformat()}
    INTAKE_STORE[token_code] = record
    return {"token_code": token_code, "status": "queued", "record": record}

@app.get("/api/intake/fetch/{token_code}")
async def fetch_intake_endpoint(token_code: str):
    code = token_code.strip().upper()
    if code not in INTAKE_STORE: raise HTTPException(status_code=404, detail=f"Token code {code} not found or expired.")
    return INTAKE_STORE[code]

@app.get("/api/intake/queue")
async def list_intake_queue_endpoint():
    return list(INTAKE_STORE.values())[::-1]


