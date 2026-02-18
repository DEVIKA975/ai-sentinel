"""AI Security Policies
Defines approved AI tools, data classification, and risk assessment rules.
"""
import os

# Approved AI endpoints (sanctioned by the organization)
# Load from environment variable (comma-separated) or use defaults
env_domains = os.getenv("APPROVED_DOMAINS", "")
if env_domains:
    APPROVED_DOMAINS = [d.strip() for d in env_domains.split(",") if d.strip()]
else:
    APPROVED_DOMAINS = [
        "internal-ai.company.local",
        "ai.company.internal",
        "approved-partner.com"
    ]

# External AI services (require scrutiny)
EXTERNAL_AI_SERVICES = [
    "chat.openai.com",
    "chatgpt.com",
    "api.openai.com",
    "api.anthropic.com",
    "claude.ai",
    "gemini.google.com",
    "api.cohere.ai",
    "bard.google.com"
]

# Known malicious domains (local fallback for demo/performance)
MALICIOUS_DOMAINS = [
    "evil-phishing-site.com",
    "malware-distributor.net",
    "suspicious-internal-proxy.info",
    "data-exfiltration-test.org"
]

# Sensitive data patterns (regex-based detection)
SENSITIVE_PATTERNS = {
    "iban": r"[A-Z]{2}[0-9]{2}[A-Z0-9]{1,30}",
    "account_number": r"\b\d{8,12}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "phone": r"\b\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b",
    "monetary_large": r"€\s*\d{1,3}(,\d{3})*(\.\d{2})?[KMB]?",
}

# Department risk profiles
DEPARTMENT_RISK_LEVELS = {
    "Fraud Detection": "high_sensitivity",
    "Investment Banking": "high_sensitivity",
    "Risk Analytics": "high_sensitivity",
    "Data Engineering": "high_sensitivity",
    "Compliance": "medium_sensitivity",
    "Customer Service": "medium_sensitivity",
    "IT Security": "medium_sensitivity",
    "HR": "low_sensitivity",
    "Marketing": "low_sensitivity",
    "Product Management": "low_sensitivity"
}

# Risk categorization rules
RISK_CATEGORIES = {
    "APPROVED": {
        "description": "Request to sanctioned internal AI platform",
        "action": "Allow",
        "score_range": (0, 20)
    },
    "LOW_RISK": {
        "description": "External AI with non-sensitive data",
        "action": "Monitor",
        "score_range": (21, 40)
    },
    "MEDIUM_RISK": {
        "description": "External AI with potentially sensitive context",
        "action": "Alert and educate user",
        "score_range": (41, 70)
    },
    "HIGH_RISK": {
        "description": "External AI with confirmed sensitive data",
        "action": "Block and notify security team",
        "score_range": (71, 90)
    },
    "CRITICAL": {
        "description": "Active data exfiltration attempt",
        "action": "Immediate block and incident response",
        "score_range": (91, 100)
    }
}

# System prompt template for LLM analysis
DETECTION_SYSTEM_PROMPT = """You are an AI security analyst for a leading financial institution.

Your task is to analyze network requests to AI services and assess their security risk level.

APPROVED AI PLATFORMS:
{approved_domains}

EXTERNAL AI SERVICES (require scrutiny):
{external_services}

RISK ASSESSMENT CRITERIA:
1. Is the endpoint approved by the organization?
2. Does the payload contain sensitive banking data (IBANs, account numbers, customer PII, financial amounts)?
3. What is the user's department sensitivity level?
4. Is the payload size unusually large (potential data dump)?

RESPONSE FORMAT (JSON):
{{
  "risk_category": "APPROVED|LOW_RISK|MEDIUM_RISK|HIGH_RISK|CRITICAL",
  "risk_score": 0-100,
  "reasoning": "Brief explanation of the risk assessment",
  "detected_sensitive_data": ["list of sensitive data types found"],
  "recommended_action": "Action to take",
  "user_message": "Friendly message to educate the user (if applicable)"
}}

Be strict but fair. The goal is to protect the organization's data while supporting legitimate AI use.
"""

def get_detection_prompt(approved_domains: list, external_services: list) -> str:
    """Generate the system prompt for GPT-4 analysis"""
    return DETECTION_SYSTEM_PROMPT.format(
        approved_domains=", ".join(approved_domains),
        external_services=", ".join(external_services)
    )
