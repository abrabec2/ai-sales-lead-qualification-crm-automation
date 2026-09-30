
import os
import requests
from dotenv import load_dotenv
from app.models.lead import LeadRequest, LeadAnalysis

load_dotenv()


def send_to_make(
    lead: LeadRequest,
    analysis: LeadAnalysis
) -> bool:
    webhook_url = os.getenv("MAKE_WEBHOOK_URL")

    if not webhook_url:
        raise ValueError("MAKE_WEBHOOK_URL is not configured")

    payload = {
        "name": lead.name,
        "email": str(lead.email),
        "company": lead.company,
        "company_size": lead.company_size,
        "message": lead.message,
        "lead_score": analysis.lead_score,
        "priority": analysis.priority,
        "recommended_action": analysis.recommended_action,
    }

    response = requests.post(
        webhook_url,
        json=payload,
        timeout=15
    )
    response.raise_for_status()

    return True
