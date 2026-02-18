"""
Ghost AI Detection Engine
Core logic for analyzing network requests and identifying Ghost AI usage.
Supports multiple LLM providers: OpenAI, Ollama (free & local)
"""

import json
import re
import os
from typing import Dict, List, Any
from urllib.parse import urlparse
from dotenv import load_dotenv
import pandas as pd

from src.policies import (
    APPROVED_DOMAINS,
    EXTERNAL_AI_SERVICES,
    MALICIOUS_DOMAINS,
    SENSITIVE_PATTERNS,
    DEPARTMENT_RISK_LEVELS,
    get_detection_prompt
)
from src.agents import SecurityAgent

# Load environment variables
load_dotenv()

class GhostAIDetector:
    """
    Ghost AI: The primary detection engine for unsanctioned AI usage.
    """
    
    def __init__(self, provider: str = None, api_key: str = None):
        # Determine LLM provider: priority is param > env > default
        self.provider = (provider or os.getenv("LLM_PROVIDER", "openai")).lower()
        self.vt_api_key = os.getenv("VIRUSTOTAL_API_KEY")
        
        if self.provider == "ollama":
            self._init_ollama()
        else:
            self._init_openai(api_key)
            
        # Initialize Phase 2 Agent
        self.agent = SecurityAgent(provider=self.provider, api_key=api_key)
    
    def _init_ollama(self):
        """Initialize Ollama (local LLM)"""
        try:
            import ollama
            self.ollama_client = ollama
            self.model = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
            print(f"✅ Using Ollama with model: {self.model}")
        except ImportError:
            raise ImportError(
                "Ollama not installed. Install with: pip install ollama\n"
                "Then download a model: ollama pull llama3.2:1b"
            )
    
    def _init_openai(self, api_key: str = None):
        """Initialize OpenAI"""
        import openai
        # Use provided key or fallback to environment
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if not self.api_key:
            print("⚠️ OpenAI API key missing. LLM features will be disabled.")
            self.client = None
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
            print(f"✅ Using OpenAI with model: {self.model}")
        
    def analyze_request(self, log_entry: Dict[str, Any], use_agent: bool = False) -> Dict[str, Any]:
        """
        Analyze a single network request for Ghost AI and malicious activity
        """
        url = log_entry.get("request_url", "")
        payload = log_entry.get("payload_snippet", "")
        department = log_entry.get("department", "Unknown")
        payload_size = log_entry.get("payload_size_kb", 0)
        
        # Enriched metadata for the agent
        pre_analysis = {
            "is_known_malicious": False,
            "vt_malicious": False,
            "vt_details": "",
            "detected_sensitive": [],
            "policy_violation": False
        }
        
        # 1. Quick pre-screening
        domain = urlparse(url).netloc
        is_approved = any(approved in domain for approved in APPROVED_DOMAINS)
        is_external_ai = any(service in domain for service in EXTERNAL_AI_SERVICES)
        pre_analysis["is_known_malicious"] = any(malicious in domain for malicious in MALICIOUS_DOMAINS)
        
        # 2. VirusTotal Integration
        if not is_approved and not is_external_ai and self.vt_api_key:
            vt_result = self._check_virustotal(domain)
            if vt_result["is_malicious"]:
                pre_analysis["vt_malicious"] = True
                pre_analysis["vt_details"] = vt_result["details"]

        # 3. Detect sensitive data patterns
        pre_analysis["detected_sensitive"] = self._detect_sensitive_data(payload)
        
        # Get department risk level
        dept_risk = DEPARTMENT_RISK_LEVELS.get(department, "medium_sensitivity")
        
        # Determine if we have a confirmed threat or suspicious activity
        is_threat = pre_analysis["is_known_malicious"] or pre_analysis["vt_malicious"]
        is_suspicious = is_external_ai or pre_analysis["detected_sensitive"] or payload_size > 100
        
        # Enrich log entry for the agent
        log_entry["pre_analysis"] = pre_analysis
        log_entry["is_approved"] = is_approved
        
        # 🛡️ IF APPROVED and no sensitive data, fast-track as safe
        if is_approved and not pre_analysis["detected_sensitive"]:
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
        
        # 🤖 Phase 2: Agentic Analysis (Handles SOAR Actions)
        if use_agent and (is_threat or is_suspicious):
            return self.agent.run(log_entry)
            
        # 🛡️ Fallback: Policy Violation (No Agent)
        if pre_analysis["is_known_malicious"]:
            return {
                "log_entry": log_entry,
                "risk_category": "CRITICAL",
                "risk_score": 95,
                "reasoning": f"Requested domain '{domain}' is in the known malicious list.",
                "detected_sensitive_data": [],
                "recommended_action": "Block access",
                "user_message": "ACCESS BLOCKED: Known malicious site.",
                "analysis_method": "policy_violation"
            }
            
        # 🛡️ Fallback: VT Hit (No Agent)
        if pre_analysis["vt_malicious"]:
            return {
                "log_entry": log_entry,
                "risk_category": "CRITICAL",
                "risk_score": 100,
                "reasoning": f"VirusTotal flagged '{domain}' as malicious.",
                "detected_sensitive_data": [],
                "recommended_action": "Immediate disconnect",
                "user_message": "CRITICAL ALERT: Malicious activity detected.",
                "analysis_method": "virustotal_threat_intel"
            }

        # For complex cases (non-agentic), use standard LLM analysis
        if is_suspicious:
            return self._llm_analysis(log_entry, pre_analysis["detected_sensitive"], dept_risk)
        
        # Default low risk for other cases
        return {
            "log_entry": log_entry,
            "risk_category": "LOW_RISK",
            "risk_score": 25,
            "reasoning": "Non-AI endpoint with minimal data",
            "detected_sensitive_data": pre_analysis["detected_sensitive"],
            "recommended_action": "Monitor",
            "user_message": None,
            "analysis_method": "rule_based"
        }
    
    def _check_virustotal(self, domain: str) -> Dict[str, Any]:
        """Check a domain against VirusTotal API"""
        import requests
        url = f"https://www.virustotal.com/api/v3/domains/{domain}"
        headers = {
            "accept": "application/json",
            "x-apikey": self.vt_api_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                stats = data['data']['attributes']['last_analysis_stats']
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                
                return {
                    "is_malicious": malicious > 0 or suspicious > 3,
                    "malicious_count": malicious,
                    "details": f"Vendors: {malicious} malicious, {suspicious} suspicious"
                }
            return {"is_malicious": False, "malicious_count": 0, "details": "No data"}
        except Exception as e:
            print(f"VirusTotal lookup failed: {str(e)}")
            return {"is_malicious": False, "malicious_count": 0, "details": "Lookup Error"}

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
        Use LLM (OpenAI or Ollama) to perform deep analysis of the request
        """
        # Prepare context
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
            if self.provider == "ollama":
                result = self._call_ollama(analysis_context)
            else:
                result = self._call_openai(analysis_context)
            
            # Add metadata
            result["log_entry"] = log_entry
            result["analysis_method"] = f"{self.provider}_analysis"
            
            return result
            
        except Exception as e:
            # Fallback to conservative assessment on error
            return {
                "log_entry": log_entry,
                "risk_category": "MEDIUM_RISK",
                "risk_score": 50,
                "reasoning": f"{self.provider.upper()} analysis failed: {str(e)}. Applying conservative risk assessment.",
                "detected_sensitive_data": detected_sensitive,
                "recommended_action": "Manual review required",
                "user_message": None,
                "analysis_method": "fallback",
                "error": str(e)
            }
    
    def _call_openai(self, context: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": get_detection_prompt(APPROVED_DOMAINS, EXTERNAL_AI_SERVICES)
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def _call_ollama(self, context: str) -> Dict[str, Any]:
        """Call Ollama (local LLM)"""
        system_prompt = get_detection_prompt(APPROVED_DOMAINS, EXTERNAL_AI_SERVICES)
        
        full_prompt = f"""{system_prompt}

{context}

Respond with ONLY valid JSON in this exact format:
{{
  "risk_category": "APPROVED or LOW_RISK or MEDIUM_RISK or HIGH_RISK or CRITICAL",
  "risk_score": 0-100,
  "reasoning": "Brief explanation",
  "detected_sensitive_data": ["list of data types"],
  "recommended_action": "Action to take",
  "user_message": "Message for user or null"
}}"""
        
        response = self.ollama_client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            options={
                "temperature": 0.1,
                "num_predict": 500
            }
        )
        
        # Extract JSON from response
        response_text = response['message']['content']
        
        # Try to parse JSON directly
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # If still can't parse, try to find JSON object
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            raise ValueError(f"Could not parse JSON from Ollama response: {response_text}")
    
    def get_analytics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate advanced analytics from batch results
        """
        if not results:
            return {}
            
        df = pd.DataFrame([
            {
                "category": r.get("risk_category", "UNKNOWN"),
                "score": r.get("risk_score", 0),
                "dept": r.get("log_entry", {}).get("department", "Unknown"),
                "sensitive": len(r.get("pre_analysis", {}).get("detected_sensitive", [])),
                "method": r.get("analysis_method", "Fast-track")
            } for r in results
        ])
        
        # Risk distribution
        risk_dist = df["category"].value_counts().to_dict()
        
        # Dept risk level (average score)
        dept_risk = df.groupby("dept")["score"].mean().to_dict()
        
        # Sensitive data types captured
        sensitive_types = {}
        for r in results:
            for s in r.get("pre_analysis", {}).get("detected_sensitive", []):
                sensitive_types[s] = sensitive_types.get(s, 0) + 1
                
        return {
            "risk_distribution": risk_dist,
            "department_risk": dept_risk,
            "sensitive_exfiltration_breakdown": sensitive_types,
            "total_threats": len(df[df["score"] > 40]),
            "avg_risk_score": df["score"].mean()
        }

    def batch_analyze(self, log_entries: List[Dict[str, Any]], use_agent: bool = False) -> List[Dict[str, Any]]:
        """
        Analyze multiple log entries
        
        Args:
            log_entries: List of log entry dictionaries
            use_agent: Whether to use agentic orchestration
            
        Returns:
            List of analysis results
        """
        results = []
        
        for entry in log_entries:
            result = self.analyze_request(entry, use_agent=use_agent)
            results.append(result)
        
        return results
    
    @staticmethod
    def load_logs_from_file(filepath: str) -> List[Dict[str, Any]]:
        """Load log entries from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
