
import pytest
from src.detector import GhostAIDetector
from src.policies import APPROVED_DOMAINS, MALICIOUS_DOMAINS

def test_internal_domain_detection():
    detector = GhostAIDetector()
    log = {
        "request_url": f"https://{APPROVED_DOMAINS[0]}/api",
        "payload_snippet": "Normal query"
    }
    result = detector.analyze_request(log, use_agent=False)
    assert result["risk_category"] == "APPROVED"
    assert result["risk_score"] < 20

def test_sensitive_data_detection():
    detector = GhostAIDetector(api_key="mock_key") # Use a mock key to avoid init warning if desired
    log = {
        "request_url": "https://external-ai.com",
        "payload_snippet": "My IBAN is NL12BANA000123456789"
    }
    result = detector.analyze_request(log, use_agent=False)
    assert "detected_sensitive" in result["log_entry"]["pre_analysis"]
    assert "iban" in result["log_entry"]["pre_analysis"]["detected_sensitive"]
    # Rule-based fallback (no real LLM) usually returns MEDIUM_RISK (50)
    assert result["risk_score"] == 50 

def test_malicious_domain_detection():
    detector = GhostAIDetector(api_key="mock_key")
    log = {
        "request_url": "https://evil-phishing-site.com/login",
        "payload_snippet": "Normal text"
    }
    result = detector.analyze_request(log, use_agent=False)
    assert result["log_entry"]["pre_analysis"]["is_known_malicious"] is True
    assert result["risk_category"] == "CRITICAL"

def test_batch_analyze_stats():
    detector = GhostAIDetector()
    logs = [
        {"request_url": "https://approved-partner.com", "payload_snippet": "ok"},
        {"request_url": "https://unknown.ai", "payload_snippet": "IBAN NL12345"}
    ]
    results = detector.batch_analyze(logs, use_agent=False)
    assert len(results) == 2
    analytics = detector.get_analytics(results)
    assert "risk_distribution" in analytics
    assert analytics["total_threats"] >= 1
