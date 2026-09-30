# AI Sales Lead Qualification & CRM Automation

An AI-powered sales automation system that analyzes incoming sales leads, scores and prioritizes them, and automatically routes them to the appropriate CRM workflow.

The application combines a FastAPI backend, LangChain, a locally hosted Ollama LLM, and Make.com workflow automation to demonstrate how AI-generated business decisions can be converted into automated downstream actions.

## Business Problem

Sales teams receive leads with different levels of purchase intent, urgency, and business value. Manually reviewing every lead can slow down response times and make prioritization inconsistent.

This project automates the qualification process by:

- Analyzing the lead's message and business context
- Identifying purchase intent
- Generating a lead score from 0–100
- Assigning HIGH, MEDIUM, or LOW priority
- Estimating AI confidence
- Producing a concise lead summary
- Selecting the appropriate next action
- Automatically sending the result into a CRM-style workflow

## Architecture

```text
Incoming Sales Lead
        |
        v
     FastAPI
        |
        v
     LangChain
        |
        v
Ollama / phi4-mini
        |
        v
Structured LeadAnalysis
        |
        v
Business Routing Rules
        |
        v
Make.com Webhook
        |
        v
      Router
   /     |      \
  v      v       v
Sales  Nurture  Human
Contact          Review
   \      |       /
          v
     Google Sheets
```

## AI Qualification Output

Each lead is converted into structured data containing:

```json
{
  "intent": "PURCHASE_INTEREST",
  "lead_score": 80,
  "priority": "HIGH",
  "confidence": 0.85,
  "summary": "The company is evaluating an AI automation platform and plans to implement a solution this quarter.",
  "recommended_action": "SALES_CONTACT"
}
```

Pydantic models enforce the expected output structure and validation rules.

## Routing Logic

The application converts AI analysis into deterministic business actions:

| Condition | Recommended Action |
|---|---|
| High-priority qualified lead | `SALES_CONTACT` |
| Medium/low-priority lead | `NURTURE` |
| Purchase interest with confidence below 0.80 | `HUMAN_REVIEW` |

This hybrid approach combines LLM reasoning with deterministic application rules so that downstream automation does not depend entirely on unrestricted model output.

## End-to-End Automation

After qualification, FastAPI sends the structured lead data to a Make.com webhook.

Make.com routes the lead based on `recommended_action`:

```text
SALES_CONTACT → Sales Contact workflow
NURTURE       → Nurture workflow
HUMAN_REVIEW  → Human Review workflow
```

Each routed lead is automatically recorded in Google Sheets, which acts as a lightweight CRM destination for the project.

## Verified Scenarios

The end-to-end workflow has been tested with real local LLM inference for all three routing paths:

| Lead Type | Score | Priority | Result |
|---|---:|---|---|
| Strong purchase intent | 80 | HIGH | SALES_CONTACT |
| No immediate purchase plans | 0 | LOW | NURTURE |
| Ambiguous purchase interest | 75 | MEDIUM | HUMAN_REVIEW |

Each result successfully passed through:

```text
FastAPI → LangChain → Ollama → Make.com → Router → Google Sheets
```

## Technology Stack

- Python
- FastAPI
- LangChain
- Ollama
- phi4-mini
- Pydantic
- Make.com
- Google Sheets
- Pytest
- HTTP/REST APIs
- python-dotenv

The LLM runs locally through Ollama, so the application does not require a paid LLM API.

## Project Structure

```text
ai-sales-lead-qualification-crm-automation/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── lead.py
│   └── services/
│       ├── lead_analyzer.py
│       └── make_webhook.py
├── tests/
│   └── test_lead_api.py
├── .gitignore
├── README.md
└── requirements.txt
```

## API Endpoint

### Analyze Lead

```http
POST /api/leads/analyze
```

The endpoint requires an API key using the `X-API-Key` request header.

Example request body:

```json
{
  "name": "Sophia Martinez",
  "email": "sophia@example.com",
  "company": "Enterprise Dynamics",
  "company_size": 900,
  "message": "We are evaluating an AI automation platform and want to purchase and implement a solution this quarter."
}
```

## Local Setup

### 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```env
LEAD_API_KEY=your_api_key
MAKE_WEBHOOK_URL=your_make_webhook_url
```

The `.env` file is excluded from Git and should never be committed.

### 4. Start Ollama

Make sure Ollama is installed and the `phi4-mini` model is available.

```bash
ollama pull phi4-mini
```

### 5. Start the API

```bash
uvicorn app.main:app --reload
```

Health check:

```http
GET /health
```

## Testing

Run the automated test suite:

```bash
python -m pytest -v
```

The test suite covers:

- High-priority sales-contact routing
- Low-priority nurture routing
- Low-confidence human-review routing
- Missing API-key authentication
- Invalid API-key authentication
- API health check

## Key Engineering Decisions

**Structured LLM output:** LangChain and Pydantic are used to constrain model responses to a predictable schema suitable for automation.

**Hybrid AI + deterministic rules:** The LLM performs contextual analysis, while Python enforces critical routing rules.

**Human-in-the-loop handling:** Leads with purchase potential but lower AI confidence are routed for human review rather than automatically acted upon.

**Local LLM inference:** Ollama provides local inference without requiring a paid external LLM API.

**Decoupled workflow automation:** FastAPI sends completed AI decisions to Make.com, allowing the AI service and downstream business workflow to remain separate.

## Future Enhancements

Potential production enhancements include:

- Integration with Salesforce or HubSpot
- Persistent lead storage in PostgreSQL
- Lead-processing dashboard
- Observability and structured logging
- Retry and dead-letter handling for failed webhook deliveries
- LLM evaluation and monitoring
- Containerization with Docker
- Cloud deployment