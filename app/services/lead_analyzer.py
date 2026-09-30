
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from app.models.lead import LeadAnalysis, LeadRequest


# Initialize the local Ollama model.
llm = ChatOllama(
    model="phi4-mini",
    temperature=0,
)

# Ensure AI responses follow our Pydantic schema.
structured_llm = llm.with_structured_output(LeadAnalysis)


# Define the lead qualification instructions.
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an AI sales lead qualification assistant.

Analyze each incoming sales lead using these factors:

1. Purchase intent
   - Is the lead clearly interested in purchasing
     or evaluating a solution?

2. Urgency
   - Does the lead mention a timeline such as
     immediately, this month, this quarter, or soon?

3. Business need
   - Does the lead describe a specific business
     problem or use case?

4. Company size
   - Larger organizations may represent
     higher-value opportunities.

Lead score:
- 80-100: HIGH priority
- 50-79: MEDIUM priority
- 0-49: LOW priority

Recommended action guidelines:
- HIGH priority: SALES_CONTACT
- MEDIUM priority: NURTURE
- LOW priority: NURTURE
- If there is potential purchase interest but confidence
  is below 0.80: HUMAN_REVIEW

The application will enforce the final routing rules.

Do not invent information that is not present in the lead.
""",
        ),
        (
            "human",
            """
Name: {name}
Company: {company}
Company size: {company_size}

Message:
{message}
""",
        ),
    ]
)


# Combine the prompt and structured LLM.
chain = prompt | structured_llm


def analyze_lead(lead: LeadRequest) -> LeadAnalysis:
    # Generate structured AI analysis.
    analysis = chain.invoke(
        {
            "name": lead.name,
            "company": lead.company,
            "company_size": lead.company_size,
            "message": lead.message,
        }
    )

    # Apply deterministic business routing rules.
    if (
        analysis.intent == "PURCHASE_INTEREST"
        and analysis.confidence < 0.80
    ):
        analysis.recommended_action = "HUMAN_REVIEW"

    elif analysis.priority == "HIGH":
        analysis.recommended_action = "SALES_CONTACT"

    else:
        analysis.recommended_action = "NURTURE"

    return analysis