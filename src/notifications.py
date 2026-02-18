"""
AI Sentinel - Notification System
Handles alerts to security teams via Slack and Microsoft Teams.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger("AI-Sentinel-Notifications")

class NotificationManager:
    """Sends high-priority alerts to security channels"""
    
    @staticmethod
    def send_slack_alert(risk_category: str, user_id: str, reasoning: str) -> bool:
        """
        Simulate sending a rich Slack message
        """
        emoji = "🔴" if risk_category == "CRITICAL" else "🟠"
        message = (
            f"{emoji} *AI SECURITY ALERT*\n"
            f"*User:* {user_id}\n"
            f"*Risk:* {risk_category}\n"
            f"*Reasoning:* {reasoning}\n"
            f"*Action Taken:* Automated analysis triggered"
        )
        
        logger.info(f"💬 SLACK ALERT SENT:\n{message}")
        return True

    @staticmethod
    def send_teams_alert(risk_category: str, user_id: str, reasoning: str) -> bool:
        """
        Simulate sending a Microsoft Teams Adaptive Card
        """
        logger.info(f"📧 TEAMS ALERT SENT for User: {user_id} (Risk: {risk_category})")
        return True

def broadcast_alert(analysis_result: Dict[str, Any]):
    """Broadcast alert to all configured channels"""
    risk = analysis_result.get("risk_category")
    if risk in ["HIGH_RISK", "CRITICAL"]:
        user = analysis_result.get("log_entry", {}).get("user_id", "Unknown")
        reason = analysis_result.get("reasoning", "No details")
        
        NotificationManager.send_slack_alert(risk, user, reason)
        NotificationManager.send_teams_alert(risk, user, reason)
