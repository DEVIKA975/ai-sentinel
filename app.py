"""
AI Sentinel - Shadow AI Detection Dashboard
Enterprise Demo - Phase 1 PoC
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

from src.detector import ShadowAIDetector

# Page configuration
st.set_page_config(
    page_title="AI Sentinel - Shadow AI Detection",
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
        st.markdown('<div class="main-header">🛡️ AI Sentinel</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-header">Shadow AI Detection & Mitigation Platform</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### SecureBank")
        st.caption("Enterprise Demo")

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
    
    st.plotly_chart(fig, use_container_width=True)

def render_timeline(results: list):
    """Render timeline of detections"""
    if not results:
        return
    
    # Prepare data
    data = []
    for r in results:
        data.append({
            'timestamp': r['log_entry']['timestamp'],
            'user': r['log_entry']['user_id'].split('@')[0],
            'risk_score': r['risk_score'],
            'category': r['risk_category']
        })
    
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
    st.plotly_chart(fig, use_container_width=True)

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
        
        st.markdown(f"**✅ Recommended Action:** {result['recommended_action']}")
        
        if result.get('user_message'):
            st.success(f"💬 **Message to User:** {result['user_message']}")

def main():
    """Main application"""
    render_header()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check for API key
        api_key_status = "✅ Configured" if os.getenv("OPENAI_API_KEY") else "❌ Missing"
        st.metric("OpenAI API Key", api_key_status)
        
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
        st.caption("Real-time Shadow AI detection metrics")
    
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
        if st.button("🔍 Analyze Shadow AI Threats", type="primary", use_container_width=True):
            with st.spinner("🤖 AI Sentinel is analyzing network traffic..."):
                try:
                    # Initialize detector
                    detector = ShadowAIDetector()
                    
                    # Analyze logs
                    results = detector.batch_analyze(logs)
                    
                    # Store in session state
                    st.session_state['results'] = results
                    
                    st.success("✅ Analysis complete!")
                    
                except Exception as e:
                    st.error(f"❌ Analysis failed: {str(e)}")
                    st.info("💡 Make sure you've created a .env file with your OPENAI_API_KEY")
                    return
        
        # Display results if available
        if 'results' in st.session_state:
            results = st.session_state['results']
            
            st.markdown("---")
            st.header("📊 Detection Results")
            
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
            st.header("🔍 Detailed Analysis")
            
            # Filter options
            filter_col1, filter_col2 = st.columns([1, 3])
            
            with filter_col1:
                risk_filter = st.multiselect(
                    "Filter by Risk",
                    options=['APPROVED', 'LOW_RISK', 'MEDIUM_RISK', 'HIGH_RISK', 'CRITICAL'],
                    default=['HIGH_RISK', 'CRITICAL', 'MEDIUM_RISK']
                )
            
            # Filter results
            if risk_filter:
                filtered_results = [r for r in results if r['risk_category'] in risk_filter]
            else:
                filtered_results = results
            
            # Sort by risk score (highest first)
            filtered_results = sorted(filtered_results, key=lambda x: x['risk_score'], reverse=True)
            
            st.caption(f"Showing {len(filtered_results)} of {len(results)} requests")
            
            # Display cards
            for idx, result in enumerate(filtered_results):
                render_result_card(result, idx)
    
    else:
        # Welcome screen
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 👋 Welcome to AI Sentinel")
            st.markdown("""
            **AI Sentinel** automatically detects and mitigates "Shadow AI" usage within your organization.
            
            **Key Features:**
            - 🔍 Real-time detection of unsanctioned AI tool usage
            - 🤖 GPT-4 powered risk analysis
            - 🛡️ Automatic sensitive data identification
            - 📊 Comprehensive metrics and reporting
            
            **Get Started:**
            1. Configure your OpenAI API key in `.env`
            2. Upload network logs or use sample data
            3. Click "Analyze" to detect Shadow AI threats
            
            **Value Delivered:**
            - Prevent data breaches before they happen
            - Redirect users to approved AI platforms
            - Maintain compliance with security policies
            """)
            
            st.info("💡 **Quick Start:** Check 'Use sample logs' in the sidebar to see a demo!")

if __name__ == "__main__":
    main()
