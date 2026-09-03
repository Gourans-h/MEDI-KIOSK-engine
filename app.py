import os, io, json, base64, qrcode, datetime, requests, re
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="MediKiosk OS • Clinical Intake & ABDM EMR", page_icon="●", layout="wide", initial_sidebar_state="collapsed")
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def inject_theme():
    st.markdown("""<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        .stApp { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; color: #1b1e13; background: #ffffff !important; }
        p, h1, h2, h3, h4, h5, h6, label { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif; color: #1b1e13; }
        [data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons, span[data-testid="stFileUploaderDropzoneIcon"] { font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important; }
        #MainMenu, footer, header { visibility: hidden !important; }
        .block-container { padding-top: 1.2rem !important; padding-bottom: 2.5rem !important; max-width: 1320px !important; }
        .brand-header { display: flex; justify-content: space-between; align-items: center; padding: 16px 24px; background: #58111A; border-radius: 14px; color: #f7f5bc !important; margin-bottom: 18px; border: 1px solid #4a0d14; }
        .brand-header, .brand-header *, .brand-header div, .brand-header span, .brand-header p { color: #f7f5bc !important; }
        .brand-pill { display: inline-flex; align-items: center; gap: 8px; background: rgba(247, 245, 188, 0.15); padding: 5px 12px; border-radius: 6px; font-size: 12px; font-weight: 700; color: #f7f5bc !important; border: 1px solid rgba(247, 245, 188, 0.3); }
        .pulse-dot { width: 7px; height: 7px; background: #f7f5bc; border-radius: 50%; display: inline-block; }
        .emergency-banner { background: #550000; border: 1px solid #58111A; border-radius: 12px; padding: 14px 18px; color: #f7f5bc; margin-bottom: 18px; display: flex; align-items: center; gap: 14px; }
        .emergency-banner * { color: #f7f5bc !important; }
        .stTabs [data-baseweb="tab-list"], div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) > div { display: flex !important; flex-direction: row !important; width: 100% !important; gap: 8px !important; background: #f7f5bc !important; padding: 6px !important; border-radius: 12px !important; border: 1px solid #d5d194 !important; margin-bottom: 18px !important; }
        .stTabs button[data-baseweb="tab"], div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) label { flex: 1 1 0% !important; height: 46px !important; display: flex !important; align-items: center !important; justify-content: center !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 14px !important; color: #595900 !important; background: transparent !important; border: none !important; cursor: pointer !important; transition: all 0.2s ease !important; outline: none !important; box-shadow: none !important; margin: 0 !important; padding: 0 !important; }
        .stTabs button[data-baseweb="tab"]:focus, .stTabs button[data-baseweb="tab"]:focus-visible, .stTabs button[data-baseweb="tab"]:active, div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) label:focus { outline: none !important; border: none !important; box-shadow: none !important; }
        .stTabs button[data-baseweb="tab"][aria-selected="true"], div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) label:has(input:checked) { background: #595900 !important; color: #f7f5bc !important; font-weight: 800 !important; }
        .stTabs button[data-baseweb="tab"][aria-selected="true"] *, div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) label:has(input:checked) * { color: #f7f5bc !important; }
        div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) span[data-testid="stRadioIndicator"], div[data-testid="stRadio"]:has(input[name="nav_tab_radio"]) div[data-testid="stWidgetLabel"] { display: none !important; }
        .abha-card { background: #595900; border-radius: 14px; padding: 18px 20px; color: #f7f5bc !important; margin-bottom: 14px; border: 1px solid #4a4a00; }
        .abha-card * { color: #f7f5bc !important; }
        .hud-card { background: #ffffff; border: 1px solid #dcd89e; border-radius: 14px; padding: 18px; margin-bottom: 14px; text-align: center; }
        .scanner-card, .emr-card { background: #faf9f6; border: 1px solid #dcd89e; border-radius: 14px; padding: 18px; margin-bottom: 14px; }
        .emr-card-title { font-size: 14px; font-weight: 800; color: #58111A !important; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px; border-bottom: 1px solid #dcd89e; padding-bottom: 8px; }
        .badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; }
        .badge-olive { background: #f7f5bc; color: #595900 !important; border: 1px solid #dcd89e; }
        .badge-red { background: #58111A; color: #f7f5bc !important; border: 1px solid #4a0d14; }
        .stTextInput input, .stTextArea textarea, div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea, input[type="text"], textarea { background-color: #fcfbf7 !important; border: 1.2px solid #82803b !important; border-radius: 8px !important; color: #1b1e13 !important; padding: 9px 12px !important; font-size: 13.5px !important; font-weight: 600 !important; outline: none !important; box-shadow: none !important; }
        .stTextInput input:focus, .stTextArea textarea:focus, div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus, input[type="text"]:focus, textarea:focus { border: 1.2px solid #58111A !important; background-color: #ffffff !important; box-shadow: 0 0 0 2px rgba(88,17,26,0.12) !important; }
        .stSelectbox div[data-baseweb="select"] > div, div[data-testid="stSelectbox"] div[data-baseweb="select"] > div { background-color: #fcfbf7 !important; border: 1.2px solid #82803b !important; border-radius: 8px !important; font-weight: 600 !important; color: #1b1e13 !important; outline: none !important; box-shadow: none !important; }
        [data-testid="stChatInput"], div[data-testid="stChatInputContainer"] { border: 1.2px solid #82803b !important; border-radius: 10px !important; background-color: #fcfbf7 !important; padding: 2px 6px !important; box-shadow: none !important; outline: none !important; }
        [data-testid="stChatInput"]:focus-within { border: 1.2px solid #58111A !important; background-color: #ffffff !important; box-shadow: 0 0 0 2px rgba(88,17,26,0.12) !important; }
        [data-testid="stChatInput"] textarea { background: transparent !important; border: none !important; color: #1b1e13 !important; font-weight: 500 !important; box-shadow: none !important; outline: none !important; }
        label, [data-testid="stWidgetLabel"] p { font-weight: 700 !important; color: #3b3d22 !important; font-size: 13px !important; margin-bottom: 3px !important; }
        .stButton button *, button[data-testid^="baseButton"] *, div[data-testid="stHorizontalBlock"] .stButton > button * { border: none !important; outline: none !important; background: transparent !important; box-shadow: none !important; }
        .stButton > button, button[data-testid^="baseButton"] { border-radius: 8px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; font-size: 13px !important; padding: 8px 16px !important; transition: all 0.2s ease !important; outline: none !important; box-shadow: none !important; }
        .stButton > button[kind="primary"], button[data-testid="baseButton-primary"] { background-color: #58111A !important; color: #f7f5bc !important; border: 1px solid #58111A !important; }
        .stButton > button[kind="primary"] *, button[data-testid="baseButton-primary"] * { color: #f7f5bc !important; }
        .stButton > button[kind="primary"]:hover { background-color: #450000 !important; border-color: #450000 !important; color: #ffffff !important; }
        .stButton > button[kind="primary"]:hover * { color: #ffffff !important; }
        .stButton > button:not([kind="primary"]), .stButton > button[kind="secondary"], button[data-testid="baseButton-secondary"] { background-color: #ffffff !important; color: #595900 !important; border: 1.2px solid #595900 !important; }
        .stButton > button:not([kind="primary"]) *, .stButton > button[kind="secondary"] *, button[data-testid="baseButton-secondary"] * { color: #595900 !important; }
        .stButton > button:not([kind="primary"]):hover, .stButton > button[kind="secondary"]):hover { background-color: #595900 !important; border-color: #595900 !important; color: #f7f5bc !important; }
        .stButton > button:not([kind="primary"]):hover *, .stButton > button[kind="secondary"]):hover * { color: #f7f5bc !important; }
        button:focus, button:focus-visible, .stTabs button:focus, .stTabs button:focus-visible { outline: none !important; box-shadow: none !important; }
        [data-testid="stChatMessage"] { background: #ffffff !important; border: 1px solid #dcd89e !important; border-left: 4px solid #595900 !important; border-radius: 10px !important; padding: 12px 16px !important; margin-bottom: 8px !important; }
        div[data-testid="stExpander"] { border: 1px solid #dcd89e !important; border-radius: 10px !important; background: #ffffff !important; margin-bottom: 12px !important; box-shadow: none !important; }
        div[data-testid="stExpander"] summary, div[data-testid="stExpander"] summary * { font-weight: 700 !important; color: #595900 !important; outline: none !important; }
        @keyframes ghost-shimmer { 0% { background-position: -600px 0; } 100% { background-position: 600px 0; } }
        .ghost-container { background: #ffffff !important; border: 1px solid #dcd89e !important; border-left: 4px solid #595900 !important; border-radius: 10px !important; padding: 14px 18px !important; margin: 6px 0 10px 0 !important; }
        .ghost-bone { background: linear-gradient(90deg, #f2efe6 0%, #faf8f2 35%, #e6e2d3 50%, #faf8f2 65%, #f2efe6 100%) !important; background-size: 1200px 100% !important; animation: ghost-shimmer 1.4s infinite linear !important; border-radius: 6px !important; display: block !important; }
        .ghost-avatar { width: 26px !important; height: 26px !important; border-radius: 50% !important; flex-shrink: 0 !important; }
        .ghost-pill-row { display: flex !important; gap: 8px !important; margin-top: 10px !important; flex-wrap: wrap !important; }
        .ghost-pill { height: 32px !important; flex: 1 1 20% !important; min-width: 90px !important; border-radius: 8px !important; }
        .thermal-slip-container { background: #ffffff; color: #1b1e13; font-family: 'JetBrains Mono', monospace; border: 1.5px dashed #595900; border-radius: 10px; padding: 22px; max-width: 420px; margin: 12px auto; }
        .thermal-token-num { font-size: 34px; font-weight: 900; letter-spacing: 2px; text-align: center; color: #58111A; margin: 8px 0; }
        .thermal-row { display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px; border-bottom: 1px dotted #e5e3b8; padding-bottom: 4px; }
    </style>""", unsafe_allow_html=True)

I18N = {
    "en": {
        "title": "MediKiosk OS", "subtitle": "Clinical Intake & ABDM EMR", "dpdp_badge": "DPDP Act 2023 & ABDM Compliant",
        "tab_kiosk": "Patient Touchscreen Kiosk", "tab_doctor": "Physician EMR & ABDM Workspace",
        "mode_label": "Select OPD Clinical Mode:", "mode_allopathy": "Allopathy (Modern Medicine)", "mode_ayush": "AYUSH (Ayurveda / Traditional)",
        "consent_title": "DPDP Act 2023 & ABDM Consent Status", "consent_body": "Patient Consent Active: Explicit authorization for ABDM FHIR R4 structuring. Ephemeral session purged post consultation.", "consent_check": "Authorized under Section 6 of DPDP Act 2023",
        "abha_title": "Ayushman Bharat Health Account", "abha_addr_label": "Patient ABHA Address", "abha_awaiting": "Awaiting ABHA Entry / Scan", "abha_manage_title": "Patient ABHA ID & Identity Management",
        "abha_placeholder": "e.g. 91-4829-1024-8831@abdm", "fresh_session_btn": "Start Fresh Kiosk Session", "scanner_title": "Prescription & Lab Report Scanner",
        "extract_btn": "Extract Medical Data via Vision AI", "extracting": "Extracting medications & entities...", "extracted_success": "Extracted successfully", "extracted_caption": "Extracted:",
        "interview_title": "Clinical Intake Interview", "listen_btn": "Listen", "quick_reply_hint": "Tap to quick reply:", "voice_expander": "Speak in Regional Language (Voice Input)", "voice_select": "Select Voice Language",
        "chat_placeholder": "Describe your symptoms...", "complete_intake_btn": "Complete Clinical Intake & Generate OPD Pass", "pass_title": "ABDM OPD GATEWAY", "facility_reg": "Facility Registry: HFR-IN-REG-9482 • DPDP Compliant",
        "issued_label": "Issued:", "queue_pass": "PATIENT OPD QUEUE PASS", "triage_queue_lbl": "Triage Queue:", "assigned_station_lbl": "Assigned Station:", "est_wait_lbl": "Est. Queue Time:", "patient_abha_lbl": "Patient ABHA:",
        "scan_instruction": "Scan Token via Hospital EMR Barcode Reader", "print_btn": "Print OPD Thermal Slip (80mm)", "next_patient_btn": "Next Patient / Reset Kiosk",
        "doctor_title": "Physician EMR & ABDM FHIR R4 Workspace", "doctor_caption": "Retrieve patient intake by Token Code, review/amend draft, and compile official ABDM FHIR R4 bundle.",
        "clinician_profile": "Attending Clinician Duty Profile (ABDM HPR)", "clinician_name": "Clinician Name", "clinician_hpr": "Healthcare Professional ID (HPR)", "clinician_bay": "Active Consultation Bay",
        "token_placeholder": "Enter Token Code (e.g. MED-101)", "queue_select_placeholder": "-- Select from Kiosk Queue --", "fetch_btn": "Fetch Patient Draft", "token_404": "Token [{token}] not found or expired.",
        "no_draft_title": "NO PATIENT INTAKE LOADED", "no_draft_desc": "Enter a Patient Token Code (e.g. MED-101) or select an active patient from the queue above.", "manual_note_btn": "Open Blank Consultation Note (Manual Entry)",
        "emr_edit_title": "Physician Review & Clinical Editing Workspace (Draft EMR)", "chief_lbl": "Chief Complaint", "hpi_lbl": "History of Present Illness (HPI)", "duration_lbl": "Duration",
        "severity_lbl": "Assessed Severity", "allergies_lbl": "Known Allergies (Comma separated)", "past_lbl": "Past Medical / Surgical History", "prakriti_lbl": "Prakriti (Constitution)", "agni_lbl": "Agni (Digestive Fire)",
        "sign_sync_btn": "Sign, Approve & Sync ABDM FHIR R4 Record", "err_blank": "Cannot compile or sign a blank EMR. Please specify a Chief Complaint before signing.", "download_fhir_btn": "Download ABDM FHIR R4 Bundle (JSON)", "inspect_fhir": "Inspect Official ABDM FHIR R4 JSON Bundle",
        "review_prompt": "Review the clinical draft above and click 'Sign, Approve & Sync ABDM FHIR R4 Record' to generate the official HL7 bundle.", "emergency_alert": "Emergency Red Flag Alert Triggered", "emergency_desc": "High-risk acute symptoms detected. Automated priority dispatch queued for Casualty / Emergency Triage."
    },
    "hi": {
        "title": "मेडीकिओस्क ओएस", "subtitle": "क्लिनिकल इनटेक एवं एबीडीएम ईएमआर", "dpdp_badge": "डीपीडीपी अधिनियम २०२३ एवं एबीडीएम अनुपालित",
        "tab_kiosk": "मरीज़ टचस्क्रीन कियोस्क", "tab_doctor": "चिकित्सक ईएमआर एवं एबीडीएम कार्यक्षेत्र",
        "mode_label": "क्लिनिकल मोड चुनें:", "mode_allopathy": "एलोपैथी (आधुनिक चिकित्सा)", "mode_ayush": "आयुष (आयुर्वेद / पारंपरिक चिकित्सा)",
        "consent_title": "डीपीडीपी अधिनियम २०२३ एवं सहमति स्थिति", "consent_body": "मरीज़ सहमति सक्रिय: एबीडीएम एफएचआईआर आर4 संरचना हेतु अधिकृत। सत्र समाप्ति पर डेटा शुद्ध कर दिया जाएगा।", "consent_check": "डीपीडीपी अधिनियम २०२३ की धारा ६ के तहत अधिकृत",
        "abha_title": "आयुष्मान भारत स्वास्थ्य खाता (ABHA)", "abha_addr_label": "मरीज़ आभा पता", "abha_awaiting": "आभा प्रविष्टि / स्कैन की प्रतीक्षा", "abha_manage_title": "मरीज़ आभा आईडी एवं पहचान प्रबंधन",
        "abha_placeholder": "उदा. 91-4829-1024-8831@abdm", "fresh_session_btn": "नया कियोस्क सत्र शुरू करें", "scanner_title": "पर्चा एवं लैब रिपोर्ट स्कैनर",
        "extract_btn": "विज़न एआई द्वारा डेटा निकालें", "extracting": "दवाएं एवं नैदानिक विवरण निकाले जा रहे हैं...", "extracted_success": "सफलतापूर्वक डेटा निकाला गया", "extracted_caption": "प्राप्त विवरण:",
        "interview_title": "क्लिनिकल इनटेक साक्षात्कार", "listen_btn": "सुनें (Listen)", "quick_reply_hint": "त्वरित उत्तर हेतु स्पर्श करें:", "voice_expander": "क्षेत्रीय भाषा में बोलें (वॉइस इनपुट)", "voice_select": "बोलने की भाषा चुनें",
        "chat_placeholder": "अपने लक्षण यहाँ विस्तार से लिखें...", "complete_intake_btn": "इनटेक पूर्ण करें एवं ओपीडी पास जारी करें", "pass_title": "एबीडीएम ओपीडी प्रवेश द्वार", "facility_reg": "स्वास्थ्य सुविधा पंजीकरण: HFR-IN-REG-9482",
        "issued_label": "जारी समय:", "queue_pass": "मरीज़ ओपीडी कतार पास", "triage_queue_lbl": "ट्रायज कतार:", "assigned_station_lbl": "आवंटित कक्ष:", "est_wait_lbl": "अनुमानित प्रतीक्षा समय:", "patient_abha_lbl": "मरीज़ आभा पता:",
        "scan_instruction": "अस्पताल ईएमआर स्कैनर द्वारा टोकन स्कैन करें", "print_btn": "थर्मल पास प्रिंट करें (80mm)", "next_patient_btn": "अगला मरीज़ / कियोस्क रीसेट",
        "doctor_title": "चिकित्सक ईएमआर एवं एबीडीएम एफएचआईआर आर4 कार्यक्षेत्र", "doctor_caption": "टोकन कोड द्वारा मरीज़ का विवरण लोड करें, समीक्षा/संपादन करें एवं आधिकारिक एबीडीएम एफएचआईआर आर4 बंडल तैयार करें।",
        "clinician_profile": "उपस्थित चिकित्सक प्रोफ़ाइल (एबीडीएम एचपीआर)", "clinician_name": "चिकित्सक का नाम", "clinician_hpr": "एचपीआर पंजीकरण आईडी", "clinician_bay": "परामर्श कक्ष / डेस्क",
        "token_placeholder": "टोकन कोड दर्ज करें (उदा. MED-101)", "queue_select_placeholder": "-- ओपीडी कतार से चुनें --", "fetch_btn": "मरीज़ विवरण प्राप्त करें", "token_404": "टोकन [{token}] सक्रिय कतार में नहीं मिला।",
        "no_draft_title": "कोई मरीज़ विवरण लोड नहीं है", "no_draft_desc": "कृपया टोकन कोड दर्ज करें (उदा. MED-101) या ऊपर दी गई कतार से मरीज़ चुनें।", "manual_note_btn": "रिक्त परामर्श नोट खोलें (मैन्युअल प्रविष्टि)",
        "emr_edit_title": "चिकित्सक समीक्षा एवं क्लिनिकल संपादन (ड्राफ्ट ईएमआर)", "chief_lbl": "मुख्य शिकायत", "hpi_lbl": "वर्तमान बीमारी का इतिहास (HPI)", "duration_lbl": "अवधि",
        "severity_lbl": "निर्धारित गंभीरता", "allergies_lbl": "ज्ञात एलर्जी (अल्पविराम द्वारा अलग करें)", "past_lbl": "पूर्व चिकित्सा / शल्य इतिहास", "prakriti_lbl": "प्रकृति (Prakriti)", "agni_lbl": "अग्नि (Agni)",
        "sign_sync_btn": "एबीडीएम एफएचआईआर आर4 रिकॉर्ड सत्यापित एवं सिंक करें", "err_blank": "रिक्त ईएमआर हस्ताक्षरित नहीं किया जा सकता।", "download_fhir_btn": "एबीडीएम एफएचआईआर आर4 बंडल डाउनलोड करें (JSON)", "inspect_fhir": "आधिकारिक एबीडीएम एफएचआईआर आर4 जेसन देखें",
        "review_prompt": "उपरोक्त ड्राफ्ट की समीक्षा करें एवं आधिकारिक बंडल हेतु 'सत्यापित एवं सिंक करें' पर क्लिक करें।", "emergency_alert": "आपातकालीन रेड-फ्लैग चेतावनी सक्रिय", "emergency_desc": "गंभीर लक्षण पाए गए। आपातकालीन आकस्मिक विभाग (Casualty) हेतु प्राथमिकता दी गई है।"
    }
}

T = lambda k: I18N.get(st.session_state.get("site_lang", "en"), I18N["en"]).get(k, k)

def render_ghost_loader() -> str:
    lbl = "● लक्षणों का विश्लेषण जारी है..." if st.session_state.get("site_lang") == "hi" else "● AI Clinical Engine analyzing symptoms & preparing questions..."
    return f"""<div class="ghost-container"><div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;"><div class="ghost-bone ghost-avatar"></div><div style="font-size:12px;font-weight:800;color:#595900;display:flex;align-items:center;gap:6px;"><span class="pulse-dot" style="background:#58111A;"></span> {lbl}</div></div><div style="display:flex;flex-direction:column;gap:8px;margin-bottom:14px;"><div class="ghost-bone" style="height:14px;width:85%;"></div><div class="ghost-bone" style="height:14px;width:60%;"></div></div><div class="ghost-pill-row"><div class="ghost-bone ghost-pill"></div><div class="ghost-bone ghost-pill"></div><div class="ghost-bone ghost-pill"></div><div class="ghost-bone ghost-pill"></div></div></div>"""

def reset_kiosk_state():
    is_ay, is_hi = st.session_state.get("intake_mode") == "AYUSH", st.session_state.get("site_lang") == "hi"
    w = ("**नमस्ते! मेडीकिओस्क आयुष में आपका स्वागत है।**" if is_ay else "**नमस्ते! मेडीकिओस्क में आपका स्वागत है।**") if is_hi else ("**Welcome to MediKiosk AYUSH Intake.**" if is_ay else "**Welcome to MediKiosk.**")
    st.session_state.chat_history = [{"role": "assistant", "content": f"{w} Describe your health concerns." if not is_hi else f"{w} कृपया अपने लक्षण बताएं।"}]
    st.session_state.intake_data = {"options": ["वात / जोड़ों में दर्द", "पित्त / जलन", "कफ / खांसी", "अग्नि / भूख में कमी"] if (is_ay and is_hi) else (["Vata / Joint Pain", "Pitta / Burning", "Kapha / Congestion", "Agni / Low Appetite"] if is_ay else (["बुखार एवं ठंड", "सीने में दर्द", "पेट दर्द / अपच", "सिरदर्द / चक्कर"] if is_hi else ["Fever & Chills", "Chest Pain / Heavy", "Stomach Ache", "Headache & Dizziness"])), "collected_summary": {"chief_complaint": "", "hpi": "", "duration": "", "severity": "Mild", "associated_symptoms": [], "allergies": [], "past_history": "", "ayush_prakriti": "Not Assessed", "ayush_agni": "Sama (Normal)"}, "is_red_flag": False}
    st.session_state.doc_data, st.session_state.last_token, st.session_state.abha_id, st.session_state["last_fhir"], st.session_state["manual_emr_mode"], st.session_state["token_404_error"] = {}, None, "", None, False, None

def generate_qr_base64(data_str: str) -> str:
    try:
        qr = qrcode.QRCode(version=1, box_size=4, border=1); qr.add_data(data_str); img = qr.make_image(fill_color="#58111A", back_color="#ffffff"); buf = io.BytesIO(); img.save(buf)
        return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"
    except Exception: return ""

def get_triage_hud():
    text, is_hi = " ".join([m["content"].lower() for m in st.session_state.chat_history if m["role"] == "user"]), st.session_state.get("site_lang") == "hi"
    if not text: return "[AWAITING]", "मरीज़ विवरण की प्रतीक्षा" if is_hi else "Awaiting Patient Intake", "ट्रायज हेतु लक्षण बताएं" if is_hi else "Describe symptoms to begin triage", "badge-olive", "सक्रिय" if is_hi else "Standing By", "#ffffff"
    for keys, tag, title_en, title_hi, desc_en, desc_hi, badge, priority_en, priority_hi, bg in [
        (["chest", "heart", "cardiac", "सीना", "छाती", "दिल"], "[CARDIAC]", "Cardiac Focus", "कार्डियक फोकस", "Chest region detected • Immediate ECG advised", "सीने से संबंधित लक्षण • ईसीजी जांच अनुशंसित", "badge-red", "Critical Priority", "आपातकालीन", "#fdf2f2"),
        (["breath", "lung", "asthma", "सांस", "दमा", "खांसी"], "[RESPIRATORY]", "Respiratory Focus", "श्वसन फोकस", "Airway distress detected", "श्वसन संबंधी कष्ट पाया गया", "badge-red", "Urgent Priority", "अति-आवश्यक", "#fdf2f2"),
        (["head", "headache", "dizzy", "सिर", "चक्कर"], "[NEUROLOGICAL]", "Neurological Focus", "न्यूरोलॉजिकल", "Cranial pain patterns detected", "सिरदर्द संबंधी लक्षण", "badge-olive", "Elevated Priority", "उच्च प्राथमिकता", "#ffffff"),
        (["stomach", "pitta", "agni", "digest", "पेट", "जलन", "अपच"], "[GASTROINTESTINAL]", "Gastrointestinal Focus", "उदर / अग्नि", "Digestive complaints detected", "पाचन / उदर संबंधी शिकायत", "badge-olive", "Elevated Priority", "उच्च प्राथमिकता", "#ffffff"),
        (["fever", "hot", "temperature", "बुखार", "तापमान"], "[INFECTION]", "Infection Focus", "संक्रमण फोकस", "Febrile symptoms detected", "बुखार के लक्षण • तापमान जांच अनुशंसित", "badge-olive", "Elevated Priority", "उच्च प्राथमिकता", "#ffffff"),
        (["vata", "joint", "knee", "leg", "वात", "जोड़", "घुटना"], "[MUSCULOSKELETAL]", "Musculoskeletal Focus", "अस्थि / वात", "Joint / Sandhivata symptoms detected", "जोड़ों / संधिवात के लक्षण", "badge-olive", "Routine Priority", "सामान्य", "#ffffff")
    ]:
        if any(k in text for k in keys): return tag, title_hi if is_hi else title_en, desc_hi if is_hi else desc_en, badge, priority_hi if is_hi else priority_en, bg
    return "[CLINICAL]", "क्लिनिकल मूल्यांकन" if is_hi else "Clinical Assessment", "विश्लेषण जारी..." if is_hi else "Analyzing conversation...", "badge-olive", "विश्लेषण जारी" if is_hi else "Analyzing", "#ffffff"

def send_chat_message(user_text: str):
    if not user_text or not str(user_text).strip(): return
    txt, is_hi = str(user_text).strip(), st.session_state.get("site_lang") == "hi"
    st.session_state.chat_history.append({"role": "user", "content": txt})
    try:
        res = requests.post(f"{API_BASE_URL}/api/chat", json={"chat_history": st.session_state.chat_history, "intake_mode": st.session_state.intake_mode.lower()}, timeout=15)
        if res.status_code == 200 and not res.json().get("error"):
            data = res.json(); st.session_state.intake_data = data
            q = data.get('next_question_hi' if is_hi else 'next_question_en') or data.get('next_question_en') or "Please describe your symptoms."
            st.session_state.chat_history.append({"role": "assistant", "content": f"**{q}**"})
            if not st.session_state.intake_data.get("options"): st.session_state.intake_data["options"] = ["हल्का (1-2 दिन)", "मध्यम (3-5 दिन)", "तीव्र", "अन्य"] if is_hi else ["Mild (1-2 days)", "Moderate (3-5 days)", "Severe", "Other"]
        else:
            fb = "**लक्षण दर्ज किए गए। क्या आपको अन्य कोई परेशानी है?**" if is_hi else "**Symptom recorded. Are you experiencing any other distress?**"
            st.session_state.chat_history.append({"role": "assistant", "content": fb}); st.session_state.intake_data["options"] = ["हां (Yes)", "नहीं (No)", "हल्का (Mild)", "गंभीर (Severe)"] if is_hi else ["Yes", "No", "Mild", "Severe"]
    except Exception:
        fb = "**जानकारी दर्ज कर ली गई है। क्या आपने इसके लिए कोई दवा ली है?**" if is_hi else "**Information recorded. Have you taken any medications previously?**"
        st.session_state.chat_history.append({"role": "assistant", "content": fb}); st.session_state.intake_data["options"] = ["हां (Yes)", "नहीं (No)", "घरेलू उपचार", "अन्य"] if is_hi else ["Yes", "No", "Home Remedy", "Other"]
    st.rerun()

for k, v in [("site_lang", "en"), ("intake_mode", "Allopathy"), ("active_tab", 0)]:
    if k not in st.session_state: st.session_state[k] = v
if "chat_history" not in st.session_state: reset_kiosk_state()

inject_theme()
c_brand, c_lang = st.columns([8, 4])
with c_brand: st.markdown(f"""<div class="brand-header"><div><div style="font-size:20px;font-weight:800;letter-spacing:0.5px;color:#f7f5bc !important;">{T("title")} <span style="font-weight:500;color:#f7f5bc !important;opacity:0.95;font-size:14px;">| {T("subtitle")}</span></div></div><div style="display:flex;align-items:center;gap:10px;"><div class="brand-pill"><span class="pulse-dot"></span> {T("dpdp_badge")}</div></div></div>""", unsafe_allow_html=True)
with c_lang:
    chosen_lang = st.radio("Language:", ["English", "हिन्दी"], horizontal=True, index=0 if st.session_state.site_lang == "en" else 1, label_visibility="collapsed")
    new_lang = "hi" if chosen_lang == "हिन्दी" else "en"
    if new_lang != st.session_state.site_lang:
        st.session_state.site_lang = new_lang
        if len(st.session_state.chat_history) == 1 and st.session_state.chat_history[0]["role"] == "assistant": reset_kiosk_state()
        st.rerun()

if st.session_state.intake_data.get("is_red_flag"):
    components.html("""<script>(function(){try{const c=new (window.AudioContext||window.webkitAudioContext)();function p(f,s,d){const o=c.createOscillator(),g=c.createGain();o.type='sawtooth';o.frequency.setValueAtTime(f,c.currentTime+s);g.gain.setValueAtTime(0.25,c.currentTime+s);g.gain.exponentialRampToValueAtTime(0.001,c.currentTime+s+d);o.connect(g);g.connect(c.destination);o.start(c.currentTime+s);o.stop(c.currentTime+s+d);}p(880,0,0.22);p(659.25,0.25,0.22);p(880,0.5,0.3);}catch(e){}})();</script>""", height=0, width=0)
    st.markdown(f"""<div class="emergency-banner"><div style="font-weight:800;font-size:14px;letter-spacing:0.5px;">[ALERT] {T("emergency_alert")}</div><div style="font-size:12.5px;opacity:0.95;">{T("emergency_desc")}</div></div>""", unsafe_allow_html=True)

tab_options = [f"[01] {T('tab_kiosk')}", f"[02] {T('tab_doctor')}"]
chosen_tab = st.radio("Navigation Tabs", tab_options, index=st.session_state.active_tab if st.session_state.active_tab in [0, 1] else 0, horizontal=True, label_visibility="collapsed", key="nav_tab_radio")
st.session_state.active_tab = 0 if chosen_tab == tab_options[0] else 1

if st.session_state.active_tab == 0:
    cm1, cm2 = st.columns(2)
    with cm1:
        sel_mode = st.radio(T("mode_label"), [T("mode_allopathy"), T("mode_ayush")], horizontal=True, index=0 if st.session_state.intake_mode == "Allopathy" else 1)
        new_mode = "Allopathy" if sel_mode == T("mode_allopathy") else "AYUSH"
        if new_mode != st.session_state.intake_mode: st.session_state.intake_mode = new_mode; reset_kiosk_state(); st.rerun()
    with cm2:
        with st.expander(f"[INFO] {T('consent_title')}", expanded=False): st.caption(T("consent_body")); st.checkbox(T("consent_check"), value=True)

    col_chat, col_hud = st.columns([7, 5], gap="large")
    with col_hud:
        cur_abha = st.session_state.abha_id.strip()
        st.markdown(f"""<div class="abha-card"><div style="font-size:11px;font-weight:800;text-transform:uppercase;display:flex;justify-content:space-between;"><span>{T("abha_title")}</span><span>[ABDM]</span></div><div style="font-size:11px;opacity:0.85;margin-top:6px;text-transform:uppercase;">{T("abha_addr_label")}</div><div style="font-size:19px;font-weight:800;font-family:'JetBrains Mono',monospace;letter-spacing:0.5px;color:{'#f7f5bc' if cur_abha else '#e5e3b8'};">{cur_abha or T("abha_awaiting")}</div></div>""", unsafe_allow_html=True)
        with st.expander(f"[ID] {T('abha_manage_title')}", expanded=True):
            st.session_state.abha_id = st.text_input(T("abha_addr_label"), value=st.session_state.abha_id, placeholder=T("abha_placeholder"))
            if st.button(f"[RESET] {T('fresh_session_btn')}", use_container_width=True): reset_kiosk_state(); st.session_state.active_tab = 0; st.rerun()

        icon_tag, title, subtitle, badge_cls, status_lbl, bg_c = get_triage_hud()
        st.markdown(f"""<div class="hud-card" style="background:{bg_c};"><div style="font-size:12px;font-weight:800;color:#595900;letter-spacing:1px;margin-bottom:4px;">{icon_tag}</div><div style="font-size:16px;font-weight:800;color:#1b1e13;margin-bottom:2px;">{title}</div><div style="font-size:12.5px;color:#494c34;margin-bottom:10px;">{subtitle}</div><div class="badge {badge_cls}">● {status_lbl}</div></div>""", unsafe_allow_html=True)
        
        st.markdown(f"""<div class="scanner-card"><div class="emr-card-title"><span>[SCANNER] {T("scanner_title")}</span></div></div>""", unsafe_allow_html=True)
        up_file = st.file_uploader(T("scanner_title"), type=["jpg", "png", "jpeg"], label_visibility="collapsed")
        if up_file:
            st.image(up_file, caption="Document Preview", use_container_width=True)
            if st.button(T("extract_btn"), use_container_width=True, type="primary"):
                with st.spinner(T("extracting")):
                    try:
                        res = requests.post(f"{API_BASE_URL}/api/scan", files={"file": (up_file.name, up_file.getvalue(), "image/jpeg")})
                        if res.status_code == 200: st.session_state.doc_data = res.json(); st.success(f"● {T('extracted_success')}")
                        else: st.error(f"Scan error: {res.text}")
                    except Exception as e: st.error(f"Connection failed: {e}")
        if st.session_state.doc_data: st.caption(f"● **{T('extracted_caption')}** {len(st.session_state.doc_data.get('medications', []))} Medications • {len(st.session_state.doc_data.get('diagnoses', []))} Diagnoses")

    with col_chat:
        mode_badge = "[AYUSH]" if st.session_state.intake_mode == "AYUSH" else "[ALLOPATHY]"
        ct1, ct2 = st.columns([8, 4])
        with ct1: st.markdown(f"### {T('interview_title')} <span style='font-size:12px;font-weight:700;color:#595900;background:#f7f5bc;padding:3px 8px;border-radius:6px;border:1px solid #595900;'>{mode_badge}</span>", unsafe_allow_html=True)
        with ct2:
            latest_msg = next((m["content"] for m in reversed(st.session_state.chat_history) if m["role"] == "assistant"), "")
            if latest_msg:
                is_hi, tts_lang = st.session_state.get('site_lang') == 'hi', 'hi-IN' if st.session_state.get('site_lang') == 'hi' else 'en-IN'
                btn_lbl, spk_lbl = ("🔊 सुनें", "🔊 बोल रहे हैं...") if is_hi else ("🔊 Listen", "🔊 Speaking...")
                clean_txt = re.sub(r'[*_#\[\]`]', '', latest_msg).strip()
                components.html(f"""<div style="display:flex;justify-content:flex-end;width:100%;"><button id="ttsBtn" onclick="speakText()" style="background:#595900;color:#f7f5bc;border:none;border-radius:6px;padding:6px 14px;font-size:12px;font-weight:700;cursor:pointer;display:inline-flex;align-items:center;gap:6px;font-family:-apple-system,sans-serif;"><span id="ttsLabel">{btn_lbl}</span></button></div><script>const textToSpeak={json.dumps(clean_txt)},targetLang="{tts_lang}";function getSynth(){{try{{if(window.parent&&window.parent.speechSynthesis)return window.parent.speechSynthesis;}}catch(e){{}}try{{if(window.top&&window.top.speechSynthesis)return window.top.speechSynthesis;}}catch(e){{}}return window.speechSynthesis;}}function speakText(){{const synth=getSynth();if(!synth)return;try{{if(synth.paused)synth.resume();synth.cancel();}}catch(e){{}}const btn=document.getElementById("ttsBtn"),label=document.getElementById("ttsLabel"),u=new SpeechSynthesisUtterance(textToSpeak);u.lang=targetLang;u.rate=0.92;try{{const v=synth.getVoices()||[],m=v.find(x=>x.lang===targetLang||x.lang.startsWith(targetLang.split('-')[0]));if(m)u.voice=m;}}catch(e){{}}u.onstart=()=>{{btn.style.background="#58111A";label.innerText="{spk_lbl}";}};u.onend=()=>{{btn.style.background="#595900";label.innerText="{btn_lbl}";}};u.onerror=()=>{{btn.style.background="#595900";label.innerText="{btn_lbl}";}};synth.speak(u);}}</script>""", height=40)

        chat_container = st.container(height=420)
        with chat_container:
            for msg in st.session_state.chat_history:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        qr_placeholder = st.empty()
        if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] != "user":
            options = st.session_state.intake_data.get("options", [])
            if options:
                st.markdown(f"<p style='font-size:12px;font-weight:700;color:#595900;margin:6px 0 2px 0;'>{T('quick_reply_hint')}</p>", unsafe_allow_html=True)
                with qr_placeholder.container():
                    cols = st.columns(min(len(options), 4))
                    for i, opt in enumerate(options[:4]):
                        if cols[i].button(opt, key=f"qr_{len(st.session_state.chat_history)}_{i}", use_container_width=True):
                            qr_placeholder.markdown(render_ghost_loader(), unsafe_allow_html=True); send_chat_message(opt)

        with st.expander(f"[MIC] {T('voice_expander')}", expanded=False):
            st.caption("Tap the microphone button below, describe your symptoms aloud, and stop recording." if st.session_state.site_lang != "hi" else "नीचे दिए गए माइक्रोफ़ोन बटन को दबाकर अपने लक्षण बोलें और रिकॉर्डिंग बंद करें।")
            recorded_voice = st.audio_input("Voice Input", label_visibility="collapsed", key="kiosk_audio_in")
            if recorded_voice:
                v_bytes, v_hash = recorded_voice.getvalue(), hash(recorded_voice.getvalue())
                if st.session_state.get("last_voice_hash") != v_hash:
                    st.session_state["last_voice_hash"] = v_hash; qr_placeholder.markdown(render_ghost_loader(), unsafe_allow_html=True)
                    with st.spinner("Transcribing voice intake..." if st.session_state.site_lang != "hi" else "आवाज़ का विश्लेषण जारी है..."):
                        try:
                            res = requests.post(f"{API_BASE_URL}/api/transcribe-audio", files={"file": ("voice_intake.wav", v_bytes, recorded_voice.type or "audio/wav")}, timeout=15)
                            if res.status_code == 200 and res.json().get("transcript"): send_chat_message(res.json()["transcript"])
                            else: st.warning("Could not detect clear speech. Please try speaking again." if st.session_state.site_lang != "hi" else "स्पष्ट आवाज़ नहीं मिली। कृपया पुनः बोलें।")
                        except Exception as e: st.error(f"Microphone connection error: {e}")

        if user_input := st.chat_input(T("chat_placeholder")): send_chat_message(user_input)

        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        if not st.session_state.get("last_token"):
            if st.button(T("complete_intake_btn"), type="primary", use_container_width=True):
                try:
                    res = requests.post(f"{API_BASE_URL}/api/intake/submit", json={"patient_abha_id": st.session_state.abha_id.strip() or "ANONYMOUS-WALKIN@abdm", "intake_mode": st.session_state.intake_mode, "clinical_summary": st.session_state.intake_data.get("collected_summary", {}), "doc_entities": st.session_state.doc_data, "is_red_flag": st.session_state.intake_data.get("is_red_flag", False), "chat_history": st.session_state.chat_history})
                    if res.status_code == 200: st.session_state.last_token = res.json()["token_code"]; st.rerun()
                except Exception as e: st.error(f"Submission failed: {e}")
        else:
            token, is_ay, is_rf = st.session_state.last_token, st.session_state.intake_mode == "AYUSH", st.session_state.intake_data.get("is_red_flag", False)
            dept = "AYUSH Triage Queue" if is_ay else ("Emergency Casualty Priority Queue" if is_rf else "General Medicine OPD Queue")
            room = "Casualty Emergency Bay" if is_rf else "Unassigned • Next Available Consultation Bay"
            t_str = datetime.datetime.now().strftime("%d-%b-%Y %I:%M %p")
            qr_b64 = generate_qr_base64(json.dumps({"token": token, "abha": st.session_state.abha_id or "ANONYMOUS@abdm", "triage_queue": dept, "time": t_str}))
            
            st.markdown(f"""<div class="thermal-slip-container" id="printableThermalSlip"><div style="text-align:center;border-bottom:2px dashed #595900;padding-bottom:10px;margin-bottom:12px;"><div style="font-size:14px;font-weight:800;letter-spacing:1px;color:#595900;">{T("pass_title")}</div><div style="font-size:10.5px;color:#494c34;">{T("facility_reg")}</div><div style="font-size:10.5px;margin-top:2px;">{T("issued_label")} <strong>{t_str}</strong></div></div><div style="font-size:11px;font-weight:700;text-align:center;text-transform:uppercase;color:#595900;">{T("queue_pass")}</div><div class="thermal-token-num">{token}</div><div class="thermal-row"><span>{T("triage_queue_lbl")}</span><strong>{dept}</strong></div><div class="thermal-row"><span>{T("assigned_station_lbl")}</span><strong>{room}</strong></div><div class="thermal-row"><span>{T("est_wait_lbl")}</span><strong style="color:{'#58111A' if is_rf else '#595900'};">{'[IMMEDIATE CASUALTY]' if is_rf else '~10-15 mins'}</strong></div><div class="thermal-row"><span>{T("patient_abha_lbl")}</span><strong>{st.session_state.abha_id or "WALKIN-GUEST@abdm"}</strong></div><div style="text-align:center;margin:12px 0 8px 0;padding:10px;background:#faf9ec;border:1px solid #dcd99c;border-radius:6px;"><img src="{qr_b64}" width="120" height="120" style="display:block;margin:0 auto 4px auto;" /><div style="font-size:9.5px;color:#494c34;">{T("scan_instruction")}</div></div></div>""", unsafe_allow_html=True)
            cp1, cp2 = st.columns(2)
            with cp1: components.html(f"""<button onclick="window.print()" style="background:#58111A;color:#f7f5bc;border:none;border-radius:8px;padding:10px;font-size:13px;font-weight:800;cursor:pointer;width:100%;">{T('print_btn')}</button>""", height=48)
            with cp2:
                if st.button(T("next_patient_btn"), use_container_width=True): reset_kiosk_state(); st.session_state.active_tab = 0; st.rerun()

else:
    st.markdown(f"### {T('doctor_title')}")
    st.caption(T("doctor_caption"))
    with st.expander(f"[HPR] {T('clinician_profile')}", expanded=False):
        cd1, cd2, cd3 = st.columns(3)
        doc_name = cd1.text_input(T("clinician_name"), value="Dr. On-Duty Medical Officer")
        doc_hpr = cd2.text_input(T("clinician_hpr"), value="HPR-IN-2026-9821")
        doc_bay = cd3.text_input(T("clinician_bay"), value="OPD Bay 01")
    
    cf1, cf2, cf3 = st.columns([4, 5, 3])
    with cf1: search_token = st.text_input(T("token_placeholder"), placeholder="e.g. MED-101", label_visibility="collapsed")
    with cf2:
        q_opts = [T("queue_select_placeholder")]
        try:
            q_res = requests.get(f"{API_BASE_URL}/api/intake/queue")
            if q_res.status_code == 200:
                for item in q_res.json(): q_opts.append(f"{item['token_code']} • {item.get('clinical_summary',{}).get('chief_complaint','Intake')[:22]}")
        except Exception: pass
        sel_q = st.selectbox(T("queue_select_placeholder"), q_opts, label_visibility="collapsed")
    with cf3:
        if st.button(T("fetch_btn"), type="primary", use_container_width=True):
            target = search_token.strip() if search_token else (sel_q.split(" • ")[0].strip() if sel_q != T("queue_select_placeholder") else "")
            if target:
                try:
                    f_res = requests.get(f"{API_BASE_URL}/api/intake/fetch/{target}")
                    if f_res.status_code == 200:
                        rec = f_res.json(); st.session_state.abha_id, st.session_state.intake_mode = rec["patient_abha_id"], rec.get("intake_mode", "Allopathy")
                        st.session_state.intake_data["collected_summary"] = rec.get("clinical_summary", {}); st.session_state.intake_data["is_red_flag"] = rec.get("is_red_flag", False)
                        st.session_state.doc_data, st.session_state.chat_history = rec.get("doc_entities", {}), rec.get("chat_history", st.session_state.chat_history)
                        st.session_state["token_404_error"], st.session_state["last_token"], st.session_state["manual_emr_mode"], st.session_state.active_tab = None, target, True, 1
                        st.success(f"● Loaded Intake for Token [{target}]"); st.rerun()
                    elif f_res.status_code == 404:
                        st.session_state["token_404_error"], st.session_state.active_tab = target, 1; st.rerun()
                except Exception as e: st.error(f"Fetch failed: {e}")
            else: st.warning("Please enter or select a Token Code.")

    if st.session_state.get("token_404_error"): st.markdown(f"""<div style="background:#58111A;color:#f7f5bc;border-radius:8px;padding:12px 16px;margin:10px 0;"><div style="font-weight:800;font-size:13px;">[404 NOT FOUND] {T('token_404').format(token=st.session_state['token_404_error'])}</div></div>""", unsafe_allow_html=True)

    summary, docs, is_ay = st.session_state.intake_data.get("collected_summary", {}), st.session_state.doc_data, st.session_state.intake_mode == "AYUSH"
    has_draft = bool(summary.get("chief_complaint") or st.session_state.get("last_token") or len([m for m in st.session_state.chat_history if m["role"] == "user"]) > 0 or st.session_state.get("manual_emr_mode"))
    
    if not has_draft:
        st.markdown(f"""<div style="background:#ffffff;border:1.5px dashed #595900;border-radius:12px;padding:28px 20px;text-align:center;margin:14px 0;"><div style="font-size:15px;font-weight:800;color:#595900;margin-bottom:4px;">{T("no_draft_title")}</div><div style="font-size:13px;color:#494c34;margin-bottom:14px;">{T("no_draft_desc")}</div></div>""", unsafe_allow_html=True)
        if st.button(T("manual_note_btn"), use_container_width=True): st.session_state["manual_emr_mode"] = True; st.session_state.active_tab = 1; st.rerun()
    else:
        st.markdown(f"""<div class="emr-card"><div class="emr-card-title">{T("emr_edit_title")}</div></div>""", unsafe_allow_html=True)
        ce1, ce2 = st.columns(2, gap="medium")
        with ce1:
            edit_chief = st.text_input(T("chief_lbl"), value=summary.get("chief_complaint", ""))
            edit_hpi = st.text_area(T("hpi_lbl"), value=summary.get("hpi", ""))
            cd1, cd2 = st.columns(2)
            edit_duration = cd1.text_input(T("duration_lbl"), value=summary.get("duration", "3 days"))
            edit_severity = cd2.selectbox(T("severity_lbl"), ["Mild", "Moderate", "Severe", "Critical Red-Flag"], index=1 if summary.get("severity") == "Moderate" else 0)
        with ce2:
            edit_allergies = st.text_input(T("allergies_lbl"), value=", ".join(summary.get("allergies", [])) if summary.get("allergies") else "None Reported")
            edit_past = st.text_area(T("past_lbl"), value=summary.get("past_history", "No prior chronic illnesses reported."))
            if is_ay:
                ca1, ca2 = st.columns(2)
                edit_prakriti, edit_agni = ca1.text_input(T("prakriti_lbl"), value=summary.get("ayush_prakriti", "Vata-Pitta")), ca2.text_input(T("agni_lbl"), value=summary.get("ayush_agni", "Vishama Agni"))
            else: edit_prakriti, edit_agni = "Not Assessed", "Sama (Normal)"

        if st.button(T("sign_sync_btn"), type="primary", use_container_width=True):
            if not edit_chief.strip(): st.error(T("err_blank"))
            else:
                updated_summary = {"chief_complaint": edit_chief, "hpi": edit_hpi, "duration": edit_duration, "severity": edit_severity, "allergies": [a.strip() for a in edit_allergies.split(",") if a.strip()], "past_history": edit_past, "ayush_prakriti": edit_prakriti, "ayush_agni": edit_agni}
                st.session_state.intake_data["collected_summary"] = updated_summary
                with st.spinner("Compiling and signing ABDM FHIR R4 Bundle..."):
                    try:
                        res = requests.post(f"{API_BASE_URL}/api/generate-fhir", params={"abha_id": st.session_state.abha_id.strip() or "ANONYMOUS-WALKIN@abdm"}, json={"clinical_summary": updated_summary, "doc_entities": docs, "practitioner_info": {"name": doc_name, "hpr_id": doc_hpr, "opd_bay": doc_bay}})
                        if res.status_code == 200: st.session_state["last_fhir"] = res.json(); st.success("● EMR signed & linked to patient ABHA registry")
                        else: st.error(f"FHIR Generation Error: {res.text}")
                    except Exception as e: st.error(f"Failed to compile EMR: {e}")

        if st.session_state.get("last_fhir"):
            fhir_data = st.session_state["last_fhir"]
            st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Patient ABHA ID", st.session_state.abha_id or "ANONYMOUS@abdm")
            m2.metric("FHIR Bundle ID", str(fhir_data.get("id", ""))[:8].upper())
            is_rf = st.session_state.intake_data.get("is_red_flag", False)
            m3.metric("Triage Status", "CRITICAL" if is_rf else "Approved & Synced", delta="Priority Triage" if is_rf else "Standard OPD")
            m4.metric("FHIR Resources Linked", len(fhir_data.get("entry", [])))
            
            cdl, cexp = st.columns([4, 8])
            with cdl:
                f_abha = (st.session_state.abha_id or "ANONYMOUS").replace('@', '_')
                st.download_button(T("download_fhir_btn"), data=json.dumps(fhir_data, indent=2), file_name=f"abdm_fhir_r4_{f_abha}.json", mime="application/json", use_container_width=True, type="primary")
            with cexp:
                with st.expander(f"[FHIR] {T('inspect_fhir')}", expanded=False): st.json(fhir_data)
        else: st.info(f"● {T('review_prompt')}")