
from unittest.mock import patch

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import os

from app.main import app
from app.models.lead import LeadAnalysis


load_dotenv()

client = TestClient(app)

API_KEY = os.environ["LEAD_API_KEY"]
HEADERS = {"X-API-Key": API_KEY}

LEAD = {
    "name": "John Smith",
    "email": "john@example.com",
    "company": "Example Company",
    "company_size": 300,
    "message": "We are interested in AI automation.",
}


@pytest.mark.parametrize(
    "intent,priority,confidence,expected_action",
    [
        ("PURCHASE_INTEREST", "HIGH", 0.92, "SALES_CONTACT"),
        ("GENERAL_INQUIRY", "LOW", 0.65, "NURTURE"),
        ("PURCHASE_INTEREST", "MEDIUM", 0.75, "HUMAN_REVIEW"),
    ],
)
def test_lead_routing(
    intent, priority, confidence, expected_action
):
    mock_analysis = LeadAnalysis(
        intent=intent,
        lead_score={
            "HIGH": 95,
            "MEDIUM": 55,
            "LOW": 25,
        }[priority],
        priority=priority,
        confidence=confidence,
        summary="Test lead analysis.",
        recommended_action="NURTURE",
    )

    with patch("app.services.lead_analyzer.chain") as mock_chain:
        mock_chain.invoke.return_value = mock_analysis

        response = client.post(
            "/api/leads/analyze",
            json=LEAD,
            headers=HEADERS,
        )

    assert response.status_code == 200
    assert response.json()["recommended_action"] == expected_action


def test_missing_api_key():
    response = client.post(
        "/api/leads/analyze",
        json=LEAD,
    )

    assert response.status_code == 401


def test_invalid_api_key():
    response = client.post(
        "/api/leads/analyze",
        json=LEAD,
        headers={"X-API-Key": "invalid-key"},
    )

    assert response.status_code == 401


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
