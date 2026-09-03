import json, os, easyocr
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()

# Initialize EasyOCR reader lazily on demand
reader = None

def get_ocr_reader():
    global reader
    if reader is None: reader = easyocr.Reader(['en', 'hi'], gpu=False)
    return reader

# Define Strict Output Schema
class Medication(BaseModel):
    name: str = Field(description="Name of the medicine")
    dosage: str = Field(description="Dosage (e.g., 500mg, 1 tab)")
    frequency: str = Field(description="How often it should be taken")
    duration: str = Field(description="For how many days")

class DocumentData(BaseModel):
    document_type: str = Field(description="Prescription, Lab Report, or Discharge Summary")
    date: str = Field(description="Date on the document or 'Unknown'")
    diagnoses: list[str] = Field(description="Any diagnoses listed")
    medications: list[Medication] = Field(description="Extracted medications")

def extract_and_structure_document(image_path: str) -> dict:
    """Step 1: Extract raw text via local OCR. Step 2: Structure via Gemini."""
    # Step 1: Run local OCR
    raw_ocr_text = "\n".join(get_ocr_reader().readtext(image_path, detail=0))
    # If OCR fails to catch text
    if not raw_ocr_text.strip(): return {"error": "No text detected by OCR engine."}

    # Step 2: Pass clean text to Gemini for clinical structuring
    prompt = """You are a medical data extraction assistant. Clean up the following raw OCR text extracted from an Indian prescription or lab report. Correct common OCR spelling errors for medicine names and structure them into the requested JSON schema.\nRAW OCR TEXT:\n"""
    try:
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            contents=[prompt, raw_ocr_text],
            config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=DocumentData, temperature=0.0)
        )
        return json.loads(response.text)
    except Exception as e:
        return {"error": str(e)}