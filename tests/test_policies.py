
import os
from src.policies import APPROVED_DOMAINS, EXTERNAL_AI_SERVICES, MALICIOUS_DOMAINS

def test_approved_domains_not_empty():
    assert len(APPROVED_DOMAINS) > 0
    # Check default internal domains are present if env is not set
    if not os.getenv("APPROVED_DOMAINS"):
        assert "ai.company.internal" in APPROVED_DOMAINS

def test_external_services_structure():
    assert "chat.openai.com" in EXTERNAL_AI_SERVICES
    assert "claude.ai" in EXTERNAL_AI_SERVICES

def test_malicious_domains_structure():
    assert "evil-phishing-site.com" in MALICIOUS_DOMAINS
