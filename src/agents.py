"""
AI Sentinel - Agentic Orchestration
Uses LangGraph to coordinate security analysis tools.
"""

import os
import json
import operator
from typing import Dict, List, Any, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from src.policies import APPROVED_DOMAINS, EXTERNAL_AI_SERVICES, get_detection_prompt
from src.webhooks import WebhookManager, simulate_create_incident
from src.notifications import broadcast_alert

# Define the state for our security agent
class AgentState(TypedDict):
    log_entry: Dict[str, Any]
    analysis: Dict[str, Any]
    provider: str
    api_key: str
    history: List[BaseMessage]
    tools_used: Annotated[List[str], operator.add]
    mitigation_actions: Annotated[List[str], operator.add]

class SecurityAgent:
    """Orchestrates security analysis using LangGraph"""
    
    def __init__(self, provider: str = "openai", api_key: str = None):
        self.provider = provider
        self.api_key = api_key
        
        # Initialize LLM
        if provider == "ollama":
            self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"), temperature=0.1)
        else:
            self.llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                temperature=0.1
            )
            
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile()

    def _create_workflow(self):
        """Build the LangGraph state machine"""
        graph = StateGraph(AgentState)
        
        # Define nodes
        graph.add_node("analyzer", self._analyze_node)
        graph.add_node("mitigator", self._mitigation_node)
        
        # Define edges
        graph.set_entry_point("analyzer")
        graph.add_edge("analyzer", "mitigator")
        graph.add_edge("mitigator", END)
        
        return graph

    def _analyze_node(self, state: AgentState):
        """Perform deep analysis using the LLM"""
        log = state["log_entry"]
        system_prompt = get_detection_prompt(APPROVED_DOMAINS, EXTERNAL_AI_SERVICES)
        pre = log.get("pre_analysis", {})
        pre_text = ""
        if pre:
            pre_text = "\nPRE-DETECTION METADATA:\n"
            if pre.get("is_known_malicious"): pre_text += "- LOCAL POLICY: Domain is on known MALICIOUS list.\n"
            if pre.get("vt_malicious"): pre_text += f"- VIRUSTOTAL: Flagged as malicious ({pre.get('vt_details')})\n"
            if pre.get("detected_sensitive"): pre_text += f"- SENSITIVE DATA: Identified {', '.join(pre['detected_sensitive'])}\n"

        user_content = f"Analyze this request: {json.dumps(log, indent=2)}\n{pre_text}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        
        response = self.llm.invoke(messages)
        
        # Parse JSON from response
        try:
            content = response.content
            # Handle potential markdown fencing
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                content = content[content.find("{"):content.rfind("}")+1]
                
            analysis = json.loads(content)
        except Exception:
            analysis = {
                "risk_category": "MEDIUM_RISK",
                "risk_score": 50,
                "reasoning": "Agent failed to parse LLM response. Defaulting to safe fallback.",
                "recommended_action": "Manual review required"
            }
            
        # DETERMINISTIC OVERRIDE: 
        # If pre-screening found a confirmed threat, force CRITICAL status
        # to ensure mitigation tools ALWAYS trigger in Phase 2.
        pre = log.get("pre_analysis", {})
        if pre.get("is_known_malicious") or pre.get("vt_malicious"):
            analysis["risk_category"] = "CRITICAL"
            analysis["risk_score"] = max(analysis.get("risk_score", 0), 95)
            analysis["reasoning"] = f"[DETERMINISTIC] Confirmed Threat detected: {analysis.get('reasoning')}"
        
        return {"analysis": analysis, "tools_used": ["llm_analyzer"], "mitigation_actions": []}

    def _mitigation_node(self, state: AgentState):
        """Trigger webhooks and notifications based on analysis"""
        analysis = state["analysis"]
        risk = analysis.get("risk_category")
        log = state["log_entry"]
        actions = []
        
        # Trigger automated mitigation if Critical
        if risk == "CRITICAL":
            ip = log.get("ip_address", "0.0.0.0")
            WebhookManager.trigger_mitigation(
                action="BLOCK_IP",
                target=ip,
                details=f"Agent detected Critical Risk: {analysis.get('reasoning')}"
            )
            actions.append(f"Firewall: Blocked IP {ip}")
            
        # Trigger Incident Creation for High/Critical
        if risk in ["HIGH_RISK", "CRITICAL"]:
            user = log.get("user_id", "Unknown")
            simulate_create_incident(user, risk)
            actions.append(f"SOC: Created Security Incident for {user}")
            
            # Broadcast notifications
            broadcast_alert(analysis)
            actions.append("Notification: Sent Slack/Teams Alert")
            
        return {"tools_used": ["mitigation_engine"], "mitigation_actions": actions}

    def run(self, log_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agentic workflow"""
        initial_state = {
            "log_entry": log_entry,
            "analysis": {},
            "provider": self.provider,
            "api_key": self.api_key,
            "history": [],
            "tools_used": [],
            "mitigation_actions": []
        }
        
        try:
            final_state = self.app.invoke(initial_state)
        except Exception as e:
            # Return partial state or fallback
            return {
                "log_entry": log_entry,
                "risk_category": "MEDIUM_RISK",
                "risk_score": 50,
                "reasoning": f"Agent workflow error: {str(e)}",
                "recommended_action": "Manual review required",
                "detected_sensitive_data": [],
                "user_message": None,
                "mitigation_actions": [],
                "agent_steps": ["error"]
            }
        
        # Ensure metadata is present
        result = final_state["analysis"]
        result["log_entry"] = log_entry
        result["analysis_method"] = f"agentic_{self.provider}"
        result["agent_steps"] = final_state["tools_used"]
        result["mitigation_actions"] = final_state.get("mitigation_actions", [])
        
        return result

class SecurityAdvisor:
    """Conversational security assistant for interpreting risk data"""
    
    def __init__(self, provider: str = "openai", api_key: str = None, vector_store = None):
        self.vector_store = vector_store
        if provider == "ollama":
            self.llm = ChatOllama(model=os.getenv("OLLAMA_MODEL", "llama3.2:1b"), temperature=0.7)
        else:
            self.llm = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                api_key=api_key or os.getenv("OPENAI_API_KEY"),
                temperature=0.7
            )
            
    def ask(self, query: str, context: List[Dict[str, Any]] = None, history: List[BaseMessage] = None) -> str:
        """Respond to user security queries with context"""
        system_prompt = """You are the AI Sentinel Security Advisor, a professional SOC analyst.
Your goal is to help users understand security threats, organizational policies, and risk metrics.

CONTEXT OF CURRENT ANALYSIS BATCH:
{current_batch}

HISTORICAL SECURITY MEMORY (from Vector DB):
{historical_memory}

POLICIES:
- Approved Internal Domains: {approved}
- External AI Services: {external}
- Malicious Domains: {malicious}

GUIDELINES:
1. Be professional, concise, and helpful.
2. If the user asks about specific threats in the context, use the data to explain the risk.
3. If the user asks about general security, provide best practices aligned with corporate policy.
4. If a request was blocked, explain WHY based on the detected sensitive data or domain reputation.
5. NEVER reveal internal API keys or credentials.
"""
        # Format CURRENT context
        current_context_str = "No active analysis data available for the current batch."
        if context:
            summary = []
            for r in context:
                summary.append(f"- User: {r.get('log_entry', {}).get('user_id')}, Risk: {r.get('risk_category')}, Reason: {r.get('reasoning')}")
            current_context_str = "\n".join(summary[:10])
            
        # Retrieve HISTORICAL context from Vector DB
        historical_context = "No historical security records available in Vector DB."
        if self.vector_store:
            historical_context = self.vector_store.search_context(query)
            
        from src.policies import MALICIOUS_DOMAINS
        
        formatted_system = system_prompt.format(
            current_batch=current_context_str,
            historical_memory=historical_context,
            approved=", ".join(APPROVED_DOMAINS),
            external=", ".join(EXTERNAL_AI_SERVICES),
            malicious=", ".join(MALICIOUS_DOMAINS)
        )
        
        messages = [SystemMessage(content=formatted_system)]
        if history:
            messages.extend(history)
        messages.append(HumanMessage(content=query))
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"I apologize, but I encountered an error processing your request: {str(e)}"
