from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LeadRequest(BaseModel):
    name: str
    email: EmailStr
    company: str
    company_size: int = Field(gt=0)
    message: str


class LeadAnalysis(BaseModel):
    intent: Literal[
        "PURCHASE_INTEREST",
        "GENERAL_INQUIRY",
        "SUPPORT_REQUEST",
        "OTHER",
    ]
    lead_score: int = Field(ge=0, le=100)
    priority: Literal["HIGH", "MEDIUM", "LOW"]
    confidence: float = Field(ge=0.0, le=1.0)
    summary: str
    recommended_action: Literal[
        "SALES_CONTACT",
        "NURTURE",
        "HUMAN_REVIEW",
    ]