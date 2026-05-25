import json
from datetime import datetime

def build_report(ctx, flags, risk_assessment, case_id):
    report = {
        "module": "metadata_integrity_check",
        "case_id": case_id,
        "timestamp": datetime.utcnow().isoformat(),
        "risk_assessment": risk_assessment,
        "flags": [{
            "risk_type": f.risk_type,
            "severity": f.severity,
            "evidence": f.evidence,
            "location": f.location,
            "review_required": f.review_required,
            "suggested_action": f.suggested_action
        } for f in flags]
    }
    with open(f"{case_id}_audit.json", 'w') as f:
        json.dump(report, f, indent=2)
    return report