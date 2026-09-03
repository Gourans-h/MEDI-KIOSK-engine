# 🏥 MediKiosk OS
> **Next-Gen AI Clinical Triage & ABDM/FHIR EMR Engine for Indian Hospital OPDs**

MediKiosk OS is an intelligent, dual-interface hospital kiosk system designed for busy outpatient departments (OPDs). It streamlines patient intake, automates clinical triage (SOCRATES protocol), extracts prescription data via Gemini Vision, and compiles everything into ABDM-compliant **FHIR R4 Bundles**.

---

## ✨ Key Features
- **🗣️ Bilingual Conversational Intake**: English and transliterated Hindi (Hinglish) with touchscreen quick replies.
- **🚨 Emergency Red Flag Detection**: Instant visual alerts for acute life-threatening symptoms (cardiac, respiratory, stroke).
- **🫀 Dynamic Anatomical HUD**: Live visual indicator adapting in real-time to organ systems (Cardiac, Respiratory, Neuro, GI, etc.).
- **📸 Gemini Multimodal OCR**: Scans paper prescriptions/lab reports and structures medicines, dosages, and diagnoses.
- **📄 ABDM FHIR R4 Bundle Generator**: Generates and downloads compliant JSON bundles linked to the patient's ABHA ID (`https://healthid.ndhm.gov.in`).

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
API_URL=http://127.0.0.1:8000
```

### 3. Launch Backend API
```bash
python -m uvicorn api:app --reload --port 8000
```

### 4. Launch Frontend Kiosk
In a separate terminal:
```bash
python -m streamlit run app.py
```
