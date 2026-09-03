import json, os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

def get_genai_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: raise ValueError("GEMINI_API_KEY is not set in .env")
    return genai.Client(api_key=api_key)

class CollectedSummary(BaseModel):
    chief_complaint: str = Field(default="Undisclosed")
    hpi: str = Field(default="")
    duration: str = Field(default="")
    severity: str = Field(default="Mild")
    associated_symptoms: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    past_history: str = Field(default="")
    ayush_prakriti: str = Field(default="Not Assessed")
    ayush_agni: str = Field(default="Sama (Normal)")
    ayush_ahara_vihara: str = Field(default="Regular")
    ayush_koshtha: str = Field(default="Madhyama")

class DialogueResponse(BaseModel):
    next_question_en: str = Field(description="Next adaptive question in English")
    next_question_hi: str = Field(description="Next adaptive question in Devanagari Hindi")
    options: List[str] = Field(default_factory=list)
    is_complete: bool = Field(default=False)
    is_red_flag: bool = Field(default=False)
    collected_summary: CollectedSummary = Field(default_factory=CollectedSummary)

ALLOPATHY_PROMPT = "You are MediKiosk Clinical AI for Allopathic OPDs. Conduct structured intake with SOCRATES protocol. Provide questions in English & Hindi (हिंदी). Provide 2-4 quick options. Set is_red_flag: true if critical."
AYUSH_PROMPT = "You are MediKiosk AYUSH AI for Ayurvedic OPDs. Assess Prakriti (Vata/Pitta/Kapha), Agni, Koshtha, and Ahara-Vihara alongside Chief Complaint. Provide questions in English & Hindi (हिंदी). Provide 2-4 quick options."

def local_adaptive_intake(chat_history: list, intake_mode: str = "allopathy") -> dict:
    msgs = [m.get("content", "") for m in chat_history if m.get("role") in ["user", "patient"]]
    turn, txt, is_ay = len(msgs), " ".join(msgs).lower(), intake_mode.lower() == "ayush"
    chief, is_rf = msgs[0] if msgs else ("Fever & Chills" if not is_ay else "Vata / Joint Pain"), any(k in txt for k in ["chest", "heart", "breath", "faint", "severe"])
    
    stages = [
        {"en": f"When did '{chief}' start and how is your appetite (Agni)?" if is_ay else f"How long have you experienced '{chief}', and is it constant or intermittent?", "hi": f"'{chief}' कब से है और आपकी भूख कैसी है?" if is_ay else f"'{chief}' कितने दिनों से है, और क्या यह लगातार बना रहता है?", "opts": ["1-2 Days • Normal", "3-5 Days • Low Appetite", "1 Week+ • Worsening", "Sudden onset today"], "comp": False},
        {"en": "How would you describe the pain or discomfort severity (1-10)?", "hi": "तकलीफ 1 से 10 के पैमाने पर कितनी तीव्र है?", "opts": ["Mild (1-3) • Dull", "Moderate (4-6) • Throbbing", "Severe (7-9) • Sharp", "Critical (10) Distress"], "comp": False},
        {"en": "Any accompanying symptoms like fever, nausea, dizziness, or breathlessness?", "hi": "क्या बुखार, उल्टी, चक्कर या सांस लेने में परेशानी जैसे कोई अन्य लक्षण हैं?", "opts": ["High Fever & Chills", "Nausea & Weakness", "Shortness of Breath", "No other symptoms"], "comp": False},
        {"en": "Any known drug allergies or chronic medical conditions (Diabetes, BP)?", "hi": "क्या आपको दवा से एलर्जी है या पुरानी बीमारी (डायबिटीज, बीपी) है?", "opts": ["No Known Allergies", "Penicillin Allergy", "Diabetes / BP", "Asthma / Dust Allergy"], "comp": False},
        {"en": "Intake complete. Click 'Complete Clinical Intake' to get your OPD token.", "hi": "विवरण पूर्ण हो चुका है। 'Complete Clinical Intake' दबाकर टोकन प्राप्त करें।", "opts": ["Review Details", "Ready for Consult"], "comp": True}
    ]
    cur = stages[min(turn, len(stages)-1)]
    return {
        "next_question_en": cur["en"], "next_question_hi": cur["hi"], "options": cur["opts"], "is_complete": cur["comp"], "is_red_flag": is_rf,
        "collected_summary": {
            "chief_complaint": chief, "hpi": f"Patient presented with {chief}.", "duration": msgs[1] if len(msgs) > 1 else "3 days",
            "severity": "Critical Red-Flag" if is_rf else (msgs[2] if len(msgs) > 2 else "Moderate"),
            "associated_symptoms": [m for m in msgs[1:3] if m != chief], "allergies": [msgs[4]] if len(msgs) > 4 and "no" not in msgs[4].lower() else [],
            "past_history": "Chronic condition reported" if "diabetes" in txt or "bp" in txt else "",
            "ayush_prakriti": "Vata-Pitta" if is_ay else "Not Assessed", "ayush_agni": "Sama (Normal)", "ayush_ahara_vihara": "Regular", "ayush_koshtha": "Madhyama"
        }
    }

def process_intake_step(chat_history: list, intake_mode: str = "allopathy") -> dict:
    merged = []
    for m in chat_history:
        txt = str(m.get("content", "")).strip()
        if not txt: continue
        r = "model" if m.get("role") in ["assistant", "model"] else "user"
        if merged and merged[-1]["role"] == r: merged[-1]["content"] += f" | {txt}"
        else: merged.append({"role": r, "content": txt})

    if merged and merged[0]["role"] == "model": merged.insert(0, {"role": "user", "content": "Start intake."})
    formatted = [types.Content(role=m["role"], parts=[types.Part.from_text(text=m["content"])]) for m in merged] or [types.Content(role="user", parts=[types.Part.from_text(text="Start consultation.")])]
    try:
        res = get_genai_client().models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=formatted,
            config=types.GenerateContentConfig(system_instruction=AYUSH_PROMPT if intake_mode.lower() == "ayush" else ALLOPATHY_PROMPT, response_mime_type="application/json", response_schema=DialogueResponse, temperature=0.2)
        )
        return json.loads(res.text)
    except Exception:
        return local_adaptive_intake(chat_history, intake_mode)