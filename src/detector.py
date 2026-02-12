"""
Shadow AI Detection Engine
Core logic for analyzing network requests and identifying Shadow AI usage.
"""

import json
import re
import os
from typing import Dict, List, Any
from urllib.parse import urlparse
import openai
from dotenv import load_dotenv

from src.policies import (
    APPROVED_DOMAINS,
    EXTERNAL_AI_SERVICES,
    SENSITIVE_PATTERNS,
    DEPARTMENT_RISK_LEVELS,
    get_detection_prompt
)

# Load environment variables
load_dotenv()

class ShadowAIDetector:
    """Detects and analyzes Shadow AI usage in network logs"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
    def analyze_request(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single network request for Shadow AI risks
        
        Args:
            log_entry: Dictionary containing request details
            
        Returns:
            Dictionary with risk assessment results
        """
        # Extract key information
        url = log_entry.get("request_url", "")
        payload = log_entry.get("payload_snippet", "")
        user_id = log_entry.get("user_id", "")
        department = log_entry.get("department", "Unknown")
        payload_size = log_entry.get("payload_size_kb", 0)
        
        # Quick pre-screening
        domain = urlparse(url).netloc
        is_approved = any(approved in domain for approved in APPROVED_DOMAINS)
        is_external_ai = any(service in domain for service in EXTERNAL_AI_SERVICES)
        
        # Detect sensitive data patterns
        detected_sensitive = self._detect_sensitive_data(payload)
        
        # Get department risk level
        dept_risk = DEPARTMENT_RISK_LEVELS.get(department, "medium_sensitivity")
        
        # If approved domain and no sensitive data, fast-track as safe
        if is_approved and not detected_sensitive:
            return {
                "log_entry": log_entry,
                "risk_category": "APPROVED",
                "risk_score": 5,
                "reasoning": "Request to approved internal AI platform with no sensitive data detected",
                "detected_sensitive_data": [],
                "recommended_action": "Allow",
                "user_message": None,
                "analysis_method": "rule_based"
            }
        
        # For complex cases, use GPT-4 analysis
        if is_external_ai or detected_sensitive or payload_size > 100:
            return self._llm_analysis(log_entry, detected_sensitive, dept_risk)
        
        # Default low risk for other cases
        return {
            "log_entry": log_entry,
            "risk_category": "LOW_RISK",
            "risk_score": 25,
            "reasoning": "Non-AI endpoint with minimal data",
            "detected_sensitive_data": detected_sensitive,
            "recommended_action": "Monitor",
            "user_message": None,
            "analysis_method": "rule_based"
        }
    
    def _detect_sensitive_data(self, text: str) -> List[str]:
        """Detect sensitive data patterns in payload"""
        found = []
        
        for data_type, pattern in SENSITIVE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                found.append(data_type)
        
        return found
    
    def _llm_analysis(self, log_entry: Dict[str, Any], 
                      detected_sensitive: List[str],
                      dept_risk: str) -> Dict[str, Any]:
        """
        Use GPT-4 to perform deep analysis of the request
        """
        # Prepare context for GPT-4
        analysis_context = f"""
NETWORK REQUEST DETAILS:
- URL: {log_entry.get('request_url')}
- User: {log_entry.get('user_id')}
- Department: {log_entry.get('department')} (Risk Level: {dept_risk})
- Payload Size: {log_entry.get('payload_size_kb')} KB
- Payload Content: "{log_entry.get('payload_snippet')}"
- Pre-detected Sensitive Data: {', '.join(detected_sensitive) if detected_sensitive else 'None'}

Analyze this request and provide a risk assessment.
"""
        
        try:
            # Call GPT-4
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": get_detection_prompt(APPROVED_DOMAINS, EXTERNAL_AI_SERVICES)
                    },
                    {
                        "role": "user",
                        "content": analysis_context
                    }
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse GPT-4 response
            result = json.loads(response.choices[0].message.content)
            
            # Add metadata
            result["log_entry"] = log_entry
            result["analysis_method"] = "gpt4_analysis"
            
            return result
            
        except Exception as e:
            # Fallback to conservative assessment on error
            return {
                "log_entry": log_entry,
                "risk_category": "MEDIUM_RISK",
                "risk_score": 50,
                "reasoning": f"GPT-4 analysis failed: {str(e)}. Applying conservative risk assessment.",
                "detected_sensitive_data": detected_sensitive,
                "recommended_action": "Manual review required",
                "user_message": None,
                "analysis_method": "fallback",
                "error": str(e)
            }
    
    def batch_analyze(self, log_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple log entries
        
        Args:
            log_entries: List of log entry dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        
        for entry in log_entries:
            result = self.analyze_request(entry)
            results.append(result)
        
        return results
    
    @staticmethod
    def load_logs_from_file(filepath: str) -> List[Dict[str, Any]]:
        """Load log entries from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
