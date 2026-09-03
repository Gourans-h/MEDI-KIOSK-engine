import uuid
from datetime import datetime, timezone

def generate_fhir_bundle(patient_abha_id: str, clinical_summary: dict, doc_entities: dict, practitioner_info: dict = None) -> dict:
    """Compiles an official ABDM/HL7 FHIR R4 JSON collection bundle with Practitioner, Encounter, Condition, Allergy, and Medication resources."""
    now_utc, bundle_id, entries = datetime.now(timezone.utc).isoformat(), str(uuid.uuid4()), []
    pref = {"identifier": {"system": "https://healthid.ndhm.gov.in", "value": patient_abha_id}}
    add = lambda res: entries.append({"fullUrl": f"urn:uuid:{uuid.uuid4()}", "resource": res})

    if practitioner_info:
        p_name, p_hpr, p_bay = practitioner_info.get("name", "Medical Officer"), practitioner_info.get("hpr_id", "HPR-IN-2026-9821"), practitioner_info.get("opd_bay", "OPD Desk 01")
        puuid = f"urn:uuid:{uuid.uuid4()}"
        entries.append({"fullUrl": puuid, "resource": {"resourceType": "Practitioner", "identifier": [{"system": "https://hpr.abdm.gov.in", "value": p_hpr}], "name": [{"text": p_name}], "extension": [{"url": "https://nrces.in/ndhm/fhir/r4/StructureDefinition/practitioner-location", "valueString": p_bay}]}})
        add({"resourceType": "Encounter", "status": "finished", "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "AMB", "display": "ambulatory"}, "subject": pref, "participant": [{"individual": {"reference": puuid, "display": p_name}}], "period": {"start": now_utc, "end": now_utc}})

    cond_notes = [{"text": f"HPI: {clinical_summary['hpi']}"}] if clinical_summary.get("hpi") else []
    if clinical_summary.get("severity"): cond_notes.append({"text": f"Severity: {clinical_summary['severity']}"})
    if clinical_summary.get("ayush_prakriti") and clinical_summary.get("ayush_prakriti") != "Not Assessed":
        cond_notes.append({"text": f"AYUSH Prakriti: {clinical_summary.get('ayush_prakriti')} | Agni: {clinical_summary.get('ayush_agni')} | Koshtha: {clinical_summary.get('ayush_koshtha', '')}"})
    add({"resourceType": "Condition", "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]}, "code": {"text": clinical_summary.get("chief_complaint", "Clinical Consultation")}, "subject": pref, "recordedDate": now_utc, **({"note": cond_notes} if cond_notes else {})})

    for a in clinical_summary.get("allergies", []):
        if a and a.lower() not in ["none", "nil", "no", "na"]:
            add({"resourceType": "AllergyIntolerance", "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-clinical", "code": "active"}]}, "verificationStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/allergyintolerance-verification", "code": "confirmed"}]}, "code": {"text": a}, "patient": pref, "recordedDate": now_utc})

    for d in doc_entities.get("diagnoses", []):
        if d: add({"resourceType": "Condition", "clinicalStatus": {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/condition-clinical", "code": "active"}]}, "code": {"text": d}, "subject": pref, "recordedDate": now_utc, "note": [{"text": "Extracted from prior medical document/prescription"}]})

    for m in doc_entities.get("medications", []):
        add({"resourceType": "MedicationStatement", "status": "active", "medicationCodeableConcept": {"text": f"{m.get('name', 'Unknown Medication')} {m.get('dosage', '')}".strip()}, "subject": pref, "dosage": [{"text": ", ".join(filter(None, [m.get("frequency", ""), m.get("duration", "")])) or "As directed"}]})

    return {"resourceType": "Bundle", "id": bundle_id, "type": "collection", "timestamp": now_utc, "entry": entries}