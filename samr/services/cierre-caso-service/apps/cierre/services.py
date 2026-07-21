import hashlib
import json


def calculate_integrity_hash(case):
    evidence = {"id": str(case.id), "patient_id": str(case.patient_id), "teleconsult_id": str(case.teleconsult_id) if case.teleconsult_id else None, "emergency_id": str(case.emergency_id) if case.emergency_id else None, "clinical_notes": case.clinical_notes}
    return hashlib.sha256(json.dumps(evidence, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def verify_case(case):
    has_source = bool(case.teleconsult_id or case.emergency_id)
    expected = calculate_integrity_hash(case) if case.clinical_notes and has_source else ""
    return {"has_clinical_notes": bool(case.clinical_notes), "has_attention_source": has_source, "integrity_valid": bool(case.integrity_hash and case.integrity_hash == expected), "ready_to_close": bool(case.clinical_notes and has_source)}
