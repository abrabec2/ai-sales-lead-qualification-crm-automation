
import os
import secrets


from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status

from app.models.lead import LeadAnalysis, LeadRequest
from app.services.lead_analyzer import analyze_lead
from app.services.make_webhook import send_to_make


load_dotenv()

API_KEY = os.getenv("LEAD_API_KEY")

if not API_KEY:
    raise RuntimeError("LEAD_API_KEY is not configured")


app = FastAPI(
    title="AI Sales Lead Qualification API",
    version="1.0.0",
)


def verify_api_key(
    x_api_key: str | None = Header(default=None),
):
    if not x_api_key or not secrets.compare_digest(
        x_api_key, API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/api/leads/analyze",
    response_model=LeadAnalysis,
    dependencies=[Depends(verify_api_key)],
)


@app.post(
    "/api/leads/analyze",
    response_model=LeadAnalysis,
    dependencies=[Depends(verify_api_key)]
)
def qualify_lead(lead: LeadRequest):
    analysis = analyze_lead(lead)
    send_to_make(lead, analysis)
    return analysis

   