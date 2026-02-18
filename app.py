"""
AI Sentinel - Ghost AI Detection Dashboard
Enterprise Demo - Phase 1 PoC
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

from src.detector import GhostAIDetector
from src.vector_db import SentinelVectorStore

# Page configuration
st.set_page_config(
    page_title="AI Sentinel - Ghost AI Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 1rem;
    }
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-weight: 600;
        font-size: 0.875rem;
    }
    .approved { background-color: #10b981; color: white; }
    .low-risk { background-color: #3b82f6; color: white; }
    .medium-risk { background-color: #f59e0b; color: white; }
    .high-risk { background-color: #ef4444; color: white; }
    .critical { background-color: #991b1b; color: white; }
</style>
""", unsafe_allow_html=True)

def get_risk_color(category: str) -> str:
    """Map risk category to color"""
    colors = {
        "APPROVED": "#10b981",
        "LOW_RISK": "#3b82f6",
        "MEDIUM_RISK": "#f59e0b",
        "HIGH_RISK": "#ef4444",
        "CRITICAL": "#991b1b"
    }
    return colors.get(category, "#6b7280")

def render_header():
    """Render application header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="main-header">🛡️ AI Sentinel</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Premium Ghost AI Monitoring & Incident Response</p>', unsafe_allow_html=True)
    
    with col2:
        st.caption("AI Sentinel - Enterprise Edition")

def render_metrics(results: list):
    """Render key metrics dashboard"""
    if not results:
        return
    
    total = len(results)
    high_critical = len([r for r in results if r['risk_category'] in ['HIGH_RISK', 'CRITICAL']])
    medium = len([r for r in results if r['risk_category'] == 'MEDIUM_RISK'])
    approved = len([r for r in results if r['risk_category'] == 'APPROVED'])
    
    # Calculate prevented breaches (high + critical)
    breaches_prevented = high_critical
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Requests",
            value=total,
            delta=None
        )
    
    with col2:
        st.metric(
            label="🚨 Critical/High Risk",
            value=high_critical,
            delta=f"{(high_critical/total*100):.1f}%" if total > 0 else "0%",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="⚠️ Medium Risk",
            value=medium,
            delta=f"{(medium/total*100):.1f}%" if total > 0 else "0%",
            delta_color="off"
        )
    
    with col4:
        st.metric(
            label="✅ Approved",
            value=approved,
            delta=f"{(approved/total*100):.1f}%" if total > 0 else "0%",
            delta_color="normal"
        )

def render_risk_distribution(results: list):
    """Render risk distribution chart"""
    if not results:
        return
    
    # Count by category
    categories = {}
    for r in results:
        cat = r['risk_category']
        categories[cat] = categories.get(cat, 0) + 1
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=list(categories.keys()),
        values=list(categories.values()),
        marker=dict(colors=[get_risk_color(cat) for cat in categories.keys()]),
        hole=.4
    )])
    
    fig.update_layout(
        title="Risk Distribution",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig)

def render_timeline(results: list):
    """Render timeline of detections"""
    if not results:
        return
    
    # Prepare data
    data = []
    for r in results:
        try:
            data.append({
                'timestamp': r['log_entry']['timestamp'],
                'user': r['log_entry']['user_id'].split('@')[0],
                'risk_score': r['risk_score'],
                'category': r['risk_category']
            })
        except (KeyError, TypeError) as e:
            # Skip entries that are missing required keys
            continue
    
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Create scatter plot
    fig = px.scatter(
        df,
        x='timestamp',
        y='risk_score',
        color='category',
        hover_data=['user'],
        color_discrete_map={
            'APPROVED': '#10b981',
            'LOW_RISK': '#3b82f6',
            'MEDIUM_RISK': '#f59e0b',
            'HIGH_RISK': '#ef4444',
            'CRITICAL': '#991b1b'
        },
        title="Risk Score Timeline"
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig)

def render_result_card(result: dict, index: int):
    """Render individual result card"""
    log = result['log_entry']
    risk_cat = result['risk_category']
    
    with st.expander(
        f"#{index+1} | {log['user_id']} → {risk_cat} (Score: {result['risk_score']})",
        expanded=False
    ):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"**🌐 URL:** `{log['request_url']}`")
            st.markdown(f"**👤 User:** {log['user_id']}")
            st.markdown(f"**🏢 Department:** {log['department']}")
            st.markdown(f"**📦 Payload Size:** {log['payload_size_kb']} KB")
            st.markdown(f"**📝 Payload Snippet:**")
            st.code(log['payload_snippet'], language=None)
        
        with col2:
            # Risk badge
            st.markdown(f'<span class="risk-badge {risk_cat.lower().replace("_", "-")}">{risk_cat}</span>', 
                       unsafe_allow_html=True)
            st.markdown(f"**Risk Score:** {result['risk_score']}/100")
            
            if result.get('detected_sensitive_data'):
                st.warning(f"🔒 Sensitive Data: {', '.join(result['detected_sensitive_data'])}")
        
        st.markdown("---")
        st.markdown(f"**🤖 Analysis:**")
        st.info(result['reasoning'])
        
        st.markdown(f"**✅ Recommended Action:** {result.get('recommended_action', 'Manual review required')}")
        
        if result.get('user_message'):
            st.success(f"💬 **Message to User:** {result['user_message']}")
            
        if result.get('agent_steps'):
            st.markdown("**🛠️ Agent Workflow Execution:**")
            steps_html = " → ".join([f"`{step}`" for step in result['agent_steps']])
            st.markdown(steps_html)
            
        if result.get('mitigation_actions'):
            st.markdown("**⚡ SOAR Actions Taken:**")
            for action in result['mitigation_actions']:
                st.code(f"EXEC: {action}", language="bash")

def render_soar_activity(results: list):
    """Render aggregate SOAR activity log for the session"""
    st.markdown("### 🛠️ SOAR Activity Log")
    
    soar_events = []
    for r in results:
        if r.get('mitigation_actions'):
            for action in r['mitigation_actions']:
                soar_events.append({
                    "user": r['log_entry'].get('user_id'),
                    "action": action,
                    "risk": r['risk_category']
                })
    
    if not soar_events:
        st.info("ℹ️ **No automated mitigation actions triggered in this batch.**")
        st.caption("Actions are only triggered for HIGH_RISK or CRITICAL threats when Agentic Logic is enabled.")
        return

    for event in soar_events:
        risk_color = "red" if event['risk'] == "CRITICAL" else "orange"
        st.markdown(f"**:{risk_color}[{event['risk']}]** | User: `{event['user']}` | Action: `{event['action']}`")

def render_behavioral_analytics(results: list):
    """Render Phase 3 Advanced Analytics"""
    st.header("🔬 Behavioral Analytics")
    
    if not results:
        return
        
    detector = GhostAIDetector()
    analytics = detector.get_analytics(results)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ghost AI Exposure Heatmap
        st.subheader("🔥 Ghost AI Exposure by Department")
        # Ensure 'department_risk' data is formatted for DataFrame
        dept_data = [{"Department": k, "Avg Risk Score": v} for k, v in analytics.get('department_risk', {}).items()]
        dept_df = pd.DataFrame(dept_data)
        if not dept_df.empty:
            fig = px.bar(dept_df, x='Department', y='Avg Risk Score', color='Avg Risk Score',
                         color_continuous_scale='Reds', title="Average Risk Exposure by Dept")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No department data available.")
        
    with col2:
        st.subheader("💸 Sensitive Data Exposure")
        # Ensure 'sensitive_exfiltration_breakdown' data is formatted for DataFrame
        sens_data = [{"Data Type": k, "Occurrences": v} for k, v in analytics.get('sensitive_exfiltration_breakdown', {}).items()]
        sens_df = pd.DataFrame(sens_data)
        if not sens_df.empty:
            fig = px.pie(sens_df, values='Occurrences', names='Data Type', hole=.3,
                         title="Types of Sensitive Data Intercepted")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sensitive data exfiltration detected in this batch.")

def render_action_center(results: list):
    """Human-in-the-loop Action Center"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛡️ Action Center (Phase 3)")
    
    pending = [r for r in results if r['risk_category'] in ['HIGH_RISK', 'MEDIUM_RISK']]
    
    if not pending:
        st.sidebar.success("✅ No pending reviews.")
        return
        
    st.sidebar.warning(f"⚠️ {len(pending)} threats require manual review")
    
    for i, p in enumerate(pending[:3]): # Show top 3
        with st.sidebar.expander(f"Review: {p.get('log_entry', {}).get('user_id', 'User')}"):
            st.write(f"**Risk:** {p['risk_category']}")
            st.write(f"**Reason:** {p['reasoning'][:100]}...")
            col1, col2 = st.columns(2)
            if col1.button("✅ Approve", key=f"app_{i}"):
                st.sidebar.toast("Action Approved & Logged")
            if col2.button("🚫 Block", key=f"blk_{i}"):
                st.sidebar.toast("Request Blocked")

def export_incident_report(results: list):
    """Generate and export a security incident report"""
    st.sidebar.markdown("---")
    if st.sidebar.button("📄 Export Incident Report"):
        report = {
            "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "total_analyzed": len(results),
                "critical_threats": len([r for r in results if r['risk_category'] == 'CRITICAL']),
                "high_risk_threats": len([r for r in results if r['risk_category'] == 'HIGH_RISK'])
            },
            "detailed_incidents": [
                {
                    "user": r.get("log_entry", {}).get("user_id"),
                    "risk": r['risk_category'],
                    "reason": r['reasoning'],
                    "actions": r.get("mitigation_actions", [])
                } for r in results if r['risk_category'] in ['CRITICAL', 'HIGH_RISK']
            ]
        }
        report_json = json.dumps(report, indent=2)
        st.sidebar.download_button(
            label="Download JSON Report",
            data=report_json,
            file_name=f"ai_sentinel_report_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

def render_architecture_map():
    """Render the Phase 2 Architecture Map in a collapsible expander"""
    with st.expander("🏗️ View System Architecture Map", expanded=False):
        st.markdown("""
        This diagram illustrates the **Agentic SOAR** workflow:
        - **LangGraph** orchestrates the analysis state.
        - **Security Agent** decides whether to trigger side-effects (Webhooks/Notifications).
        """)
        
        mermaid_code = """
        graph TD
            User((Log Entry)) --> Detector[GhostAIDetector]
            Detector --> Agent[LangGraph Security Agent]
            
            subgraph "Agent Orchestration"
                Agent --> Analyzer[analyzer node]
                Analyzer --> Mitigator[mitigator node]
            end
            
            Mitigator --> |CRITICAL| Webhook[Webhook Manager]
            Mitigator --> |HIGH/CRITICAL| Notify[Notification Manager]
            
            Webhook --> |Firewall Action| FW[Block IP / Firewall]
            Webhook --> |SOC Action| Incident[Create Incident]
            Notify --> |Alert| Slack[Slack / Teams]
            
            Mitigator --> Result[Final Risk Report]
        """
        st.write(f"```mermaid\n{mermaid_code}\n```")
        st.info("💡 The 'Chain of Thought' steps seen in detailed cards represent the nodes executed in this graph.")

def main():
    """Main application"""
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Provider Settings")
        
        # Provider selection
        llm_provider = st.radio(
            "Select LLM Provider",
            options=["OpenAI", "Ollama"],
            index=1 if os.getenv("LLM_PROVIDER") == "ollama" else 0,
            help="Choose between cloud processing (OpenAI) or local processing (Ollama)"
        )
        
        provider_api_key = None
        if llm_provider == "OpenAI":
            use_default_key = st.checkbox("Use backend API key", value=True)
            if not use_default_key:
                provider_api_key = st.text_input("Enter OpenAI API Key", type="password")
            else:
                provider_api_key = os.getenv("OPENAI_API_KEY")
                if provider_api_key:
                    st.success("✅ Backend key found")
                else:
                    st.error("❌ No backend key found")
        else:
            st.info("🏠 Running locally via Ollama")
            st.caption(f"Model: {os.getenv('OLLAMA_MODEL', 'llama3.2:1b')}")
        
        st.markdown("---")
        st.header("🤖 Execution Mode")
        use_agent = st.toggle(
            "Execute Agentic Logic (Phase 2)", 
            value=True,
            help="Uses LangGraph orchestration, triggers webhooks and notifications for Critical threats"
        )
        
        st.markdown("---")
        st.markdown("### 📊 Upload Network Logs")
        st.caption("Upload JSON file containing network request logs")
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a JSON file",
            type=['json'],
            help="Upload network logs in JSON format"
        )
        
        # Or use sample data
        use_sample = st.checkbox("Use sample logs", value=True)
        
        st.markdown("---")
        st.markdown("### 🎯 Quick Stats")
        st.caption("Real-time Ghost AI detection metrics")
    
    # Main content area
    if use_sample or uploaded_file:
        # Load logs
        if use_sample:
            sample_path = "data/sample_logs.json"
            if os.path.exists(sample_path):
                with open(sample_path, 'r') as f:
                    logs = json.load(f)
                st.info(f"📁 Loaded {len(logs)} sample log entries")
            else:
                st.error(f"Sample file not found at {sample_path}")
                return
        else:
            logs = json.load(uploaded_file)
            st.success(f"📁 Uploaded {len(logs)} log entries")
        
        # Analyze button
        if st.button("🔍 Analyze Ghost AI Threats", type="primary", use_container_width=True):
            with st.spinner("🤖 AI Sentinel is analyzing network traffic..."):
                try:
                    # Initialize detector with user settings
                    detector = GhostAIDetector(
                        provider=llm_provider.lower(),
                        api_key=provider_api_key
                    )
                    
                    # Analyze logs
                    results = detector.batch_analyze(logs, use_agent=use_agent)
                    
                    # Store in session state
                    st.session_state['results'] = results
                    
                    # Phase 5: Index into Vector DB
                    if 'vector_store' not in st.session_state:
                        st.session_state['vector_store'] = SentinelVectorStore()
                    
                    with st.spinner("🧠 Indexing results into Vector Memory..."):
                        st.session_state['vector_store'].add_log_entries(results)
                    
                    st.success("✅ Analysis and Indexing complete!")
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("💡 Make sure you've created a .env file with your OPENAI_API_KEY")
                    return
        
        if 'results' in st.session_state:
            results = st.session_state['results']
            
            # Phase 3: Action Center & Export
            render_action_center(results)
            export_incident_report(results)
            
            st.markdown("---")
            
            # Dashboard Tabs
            tab1, tab2, tab3 = st.tabs(["📊 Security Dashboard", "🚨 Incident Response", "💬 Security Advisor"])
            
            with tab1:
                st.header("🏢 Departmental Ghost AI Trends")
                # Metrics
                render_metrics(results)
                
                st.markdown("---")
                
                # Charts
                col1, col2 = st.columns(2)
                with col1:
                    render_risk_distribution(results)
                with col2:
                    render_timeline(results)
                
                st.markdown("---")
                render_behavioral_analytics(results)
                
                st.markdown("---")
                st.header("🔍 Detailed Analysis")
                
                # Filter options
                filter_col1, filter_col2 = st.columns([1, 3])
                with filter_col1:
                    risk_filter = st.multiselect(
                        "Filter by Risk",
                        options=['APPROVED', 'LOW_RISK', 'MEDIUM_RISK', 'HIGH_RISK', 'CRITICAL'],
                        default=['HIGH_RISK', 'CRITICAL', 'MEDIUM_RISK']
                    )
                
                # Filter & Sort
                if risk_filter:
                    filtered_results = [r for r in results if r['risk_category'] in risk_filter]
                else:
                    filtered_results = results
                filtered_results = sorted(filtered_results, key=lambda x: x['risk_score'], reverse=True)
                
                st.caption(f"Showing {len(filtered_results)} of {len(results)} requests")
                for idx, result in enumerate(filtered_results):
                    render_result_card(result, idx)
            
            with tab2:
                render_soar_activity(results)

            with tab3:
                st.header("💬 Security Advisor")
                st.markdown("""
                Ask our Virtual Security Assistant anything about the current analysis, organizational policies, or general security best practices.
                """)
                
                from src.agents import SecurityAdvisor
                from langchain_core.messages import HumanMessage, AIMessage
                
                # Initialize advisor and history
                if 'advisor' not in st.session_state:
                    # Initialize Vector Store if not already done
                    if 'vector_store' not in st.session_state:
                        st.session_state['vector_store'] = SentinelVectorStore()
                        
                    st.session_state.advisor = SecurityAdvisor(
                        provider=llm_provider.lower(),
                        api_key=provider_api_key,
                        vector_store=st.session_state['vector_store']
                    )
                if 'chat_history' not in st.session_state:
                    st.session_state.chat_history = []
                
                # Display chat messages
                for message in st.session_state.chat_history:
                    if isinstance(message, HumanMessage):
                        with st.chat_message("user"):
                            st.markdown(message.content)
                    else:
                        with st.chat_message("assistant"):
                            st.markdown(message.content)
                
                # Chat input
                if prompt := st.chat_input("How can I help you keep our organization secure?"):
                    # Add user message to history
                    st.session_state.chat_history.append(HumanMessage(content=prompt))
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    
                    # Generate response
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            response = st.session_state.advisor.ask(
                                query=prompt,
                                context=results,
                                history=st.session_state.chat_history[-5:] # Last 5 for context
                            )
                            st.markdown(response)
                            st.session_state.chat_history.append(AIMessage(content=response))
    
    else:
        # Welcome screen
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 👋 Welcome to AI Sentinel")
            st.markdown("""
            **AI Sentinel** automatically detects and mitigates "Ghost AI" usage within your organization.
            
            **Key Features:**
            - 🔍 Real-time detection of unsanctioned AI tool usage
            - 🤖 GPT-4 powered risk analysis
            - 🛡️ Automatic sensitive data identification
            - 📊 Comprehensive metrics and reporting
            
            **Get Started:**
            1. Configure your OpenAI API key in `.env`
            2. Upload network logs or use sample data
            3. Click "Analyze" to detect Ghost AI threats
            
            **Value Delivered:**
            - Prevent data breaches before they happen
            - Redirect users to approved AI platforms
            - Maintain compliance with security policies
            """)
            
            st.info("💡 **Quick Start:** Check 'Use sample logs' in the sidebar to see a demo!")

if __name__ == "__main__":
    main()
