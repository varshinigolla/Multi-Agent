
import streamlit as st
import asyncio
import time
import base64
from typing import Dict, Any, List
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


from orchestrator import MultiAgentOrchestrator, TaskStatus
from agents import AgentStatus


st.set_page_config(
    page_title="Multi-Agent Financial Analysis",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    .agent-status {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin: 0.25rem 0;
        font-weight: bold;
    }
    .status-pending { background-color: #f0f2f6; color: #666; }
    .status-working { background-color: #fff3cd; color: #856404; }
    .status-completed { background-color: #d4edda; color: #155724; }
    .status-error { background-color: #f8d7da; color: #721c24; }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
    }
    .chart-container {
        border: 1px solid #dee2e6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class StreamlitUI:
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        
    def run(self):
        """Main Streamlit application"""

        st.title("🤖 Multi-Agent Financial Analysis System")
        st.markdown("**Intelligent financial analysis powered by specialized AI agents**")
        

        self._create_sidebar()
        
       
        self._create_main_content()
        
        # Footer
        st.markdown("---")
        st.markdown("*Powered by OpenAI GPT-4o and specialized financial analysis agents*")

    def _create_sidebar(self):
        """Create the sidebar with agent status and system info"""
        with st.sidebar:
            st.header("🤖 Agent Status")
            
           
            status = self.orchestrator.get_status()
            
           
            status_color = {
                "pending": "🟡",
                "planning": "🔵", 
                "executing": "🟠",
                "completed": "🟢",
                "error": "🔴",
                "waiting_for_clarification": "🟡"
            }
            
            st.markdown(f"**System Status:** {status_color.get(status['status'], '⚪')} {status['status'].title()}")
            
            if status['current_task']:
                st.markdown(f"**Current Task:** {status['current_task']}")
            
            st.markdown("---")
            
            # Agent statuses
            st.subheader("Agent Status")
            for agent_id, agent_status in status['agent_status'].items():
                self._display_agent_status(agent_id, agent_status)
            
            st.markdown("---")
            
           
            st.subheader("Available Agents")
            for agent_id, agent in self.orchestrator.agents.items():
                with st.expander(f"🤖 {agent.role}"):
                    st.markdown(f"**ID:** {agent.agent_id}")
                    st.markdown(f"**Description:** {agent.description}")
                    st.markdown("**Capabilities:**")
                    for capability in agent.get_capabilities():
                        st.markdown(f"• {capability}")

    def _display_agent_status(self, agent_id: str, status: str):
        """Display individual agent status"""
        status_icons = {
            "pending": "⚪",
            "working": "🔄", 
            "completed": "✅",
            "error": "❌"
        }
        
        status_colors = {
            "pending": "status-pending",
            "working": "status-working",
            "completed": "status-completed", 
            "error": "status-error"
        }
        
        icon = status_icons.get(status, "⚪")
        color_class = status_colors.get(status, "status-pending")
        
        st.markdown(f'<div class="agent-status {color_class}">{icon} {agent_id.replace("_", " ").title()}: {status.title()}</div>', 
                   unsafe_allow_html=True)

    def _create_main_content(self):
        """Create the main content area"""
       
        st.header("📝 Enter Your Financial Analysis Request")
        
       
        with st.expander("💡 Example Requests"):
            examples = [
                "Analyze profit trends for the last 3 quarters",
                "Create charts showing segment performance",
                "Summarize financial performance by country",
                "Compare product profitability",
                "Get a comprehensive financial analysis report"
            ]
            for example in examples:
                if st.button(f"📋 {example}", key=f"example_{hash(example)}"):
                    st.session_state.user_request = example
        
        
        user_request = st.text_area(
            "Describe what financial analysis you need:",
            value=st.session_state.get('user_request', ''),
            height=100,
            placeholder="e.g., 'Analyze profit trends and create visualizations for the last quarter'"
        )
        
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("🚀 Analyze", type="primary"):
                if user_request.strip():
                    self._process_request(user_request.strip())
                else:
                    st.error("Please enter a request first!")
        
        with col2:
            if st.button("🧹 Clear"):
                st.session_state.clear()
                st.rerun()
        
       
        if 'analysis_result' in st.session_state:
            self._display_results(st.session_state.analysis_result)

    def _process_request(self, request: str):
        """Process the user request"""
        with st.spinner("🔄 Processing your request..."):
           
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            try:
               
                status_placeholder.info("📋 Planning task...")
                
               
                result = asyncio.run(self.orchestrator.process_request(request))
                
               
                if result.get("status") == "completed":
                    status_placeholder.success("✅ Analysis completed!")
                    st.session_state.analysis_result = result
                elif result.get("status") == "clarification_needed":
                    status_placeholder.warning("❓ Clarification needed")
                    self._handle_clarification(result)
                elif result.get("status") == "error":
                    status_placeholder.error(f"❌ Error: {result.get('error', 'Unknown error')}")
                else:
                    status_placeholder.warning(f"⚠️ Unexpected status: {result.get('status')}")
                
            except Exception as e:
                status_placeholder.error(f"❌ System error: {str(e)}")
                st.exception(e)

    def _handle_clarification(self, result: Dict[str, Any]):
        """Handle clarification requests"""
        st.warning("❓ **Clarification Needed**")
        
        questions = result.get("questions", [])
        clarification_answers = {}
        
        for i, question in enumerate(questions):
            answer = st.text_input(f"**Question {i+1}:** {question}", key=f"clarification_{i}")
            if answer:
                clarification_answers[f"question_{i+1}"] = answer
        
        if st.button("✅ Submit Clarification", key="submit_clarification"):
            if len(clarification_answers) == len(questions):
                with st.spinner("🔄 Processing with clarification..."):
                    updated_result = asyncio.run(
                        self.orchestrator.handle_clarification(clarification_answers)
                    )
                    
                    if updated_result.get("status") == "completed":
                        st.success("✅ Analysis completed with clarification!")
                        st.session_state.analysis_result = updated_result
                        st.rerun()
                    else:
                        st.error(f"❌ Error after clarification: {updated_result.get('error', 'Unknown error')}")
            else:
                st.error("Please answer all clarification questions!")

    def _display_results(self, result: Dict[str, Any]):
        """Display analysis results"""
        st.header("📊 Analysis Results")
        
       
        tabs = st.tabs(["📋 Summary", "📈 Analysis", "📊 Charts", "💰 Data", "🤖 Execution"])
        
        with tabs[0]:  
            self._display_summary(result.get("summary"))
        
        with tabs[1]:  # Analysis
            self._display_analysis_details(result.get("analysis", {}))
        
        with tabs[2]:  # Charts
            self._display_charts(result.get("visualizations", {}))
        
        with tabs[3]:  # Data
            self._display_financial_data(result.get("financial_data", {}))
        
        with tabs[4]:  # Execution
            self._display_execution_status(result)

    def _display_summary(self, summary: str):
        """Display the summary"""
        if summary:
            st.markdown(summary)
        else:
            st.info("No summary available")

    def _display_analysis_details(self, analysis: Dict[str, Any]):
        """Display detailed analysis"""
        if not analysis:
            st.info("No analysis data available")
            return
        
       
        for key, value in analysis.items():
            if isinstance(value, dict):
                with st.expander(f"📊 {key.replace('_', ' ').title()}"):
                    for sub_key, sub_value in value.items():
                       
                        if isinstance(sub_key, tuple):
                            sub_key_str = str(sub_key)
                        else:
                            sub_key_str = sub_key.replace('_', ' ').title()
                        
                        if isinstance(sub_value, (int, float)):
                            st.metric(sub_key_str, f"{sub_value:,.2f}")
                        elif isinstance(sub_value, (list, tuple)):
                          
                            if len(sub_value) > 0 and isinstance(sub_value[0], tuple):
                            
                                st.write(f"**{sub_key_str}:**")
                                for item in sub_value[:5]:  # Show first 5 items
                                    st.write(f"  {item}")
                                if len(sub_value) > 5:
                                    st.write(f"  ... and {len(sub_value) - 5} more")
                            else:
                                st.write(f"**{sub_key_str}:** {sub_value}")
                        else:
                            st.write(f"**{sub_key_str}:** {sub_value}")
            elif isinstance(value, (int, float)):
                
                if isinstance(key, tuple):
                    key_str = str(key)
                else:
                    key_str = key.replace('_', ' ').title()
                st.metric(key_str, f"{value:,.2f}")
            elif isinstance(value, (list, tuple)):
               
                if isinstance(key, tuple):
                    key_str = str(key)
                else:
                    key_str = key.replace('_', ' ').title()
                
                if len(value) > 0 and isinstance(value[0], tuple):
                    # Handle nested tuples (like from pandas groupby)
                    st.write(f"**{key_str}:**")
                    for item in value[:5]:  # Show first 5 items
                        st.write(f"  {item}")
                    if len(value) > 5:
                        st.write(f"  ... and {len(value) - 5} more")
                else:
                    st.write(f"**{key_str}:** {value}")
            else:
               
                if isinstance(key, tuple):
                    key_str = str(key)
                else:
                    key_str = key.replace('_', ' ').title()
                st.write(f"**{key_str}:** {value}")

    def _display_charts(self, visualizations: Dict[str, Any]):
        """Display charts"""
        if not visualizations:
            st.info("No charts available")
            return
        
        for chart_name, chart_data in visualizations.items():
            if isinstance(chart_data, dict) and chart_data.get("type") == "plotly":
                st.subheader(chart_data.get("title", chart_name.replace('_', ' ').title()))
                
               
                try:
                    html_content = base64.b64decode(chart_data["data"]).decode('utf-8')
                    
                   
                   
                    st.components.v1.html(html_content, height=500)
                    
                except Exception as e:
                    st.error(f"Error displaying chart: {e}")
                    st.info("Chart data is available but cannot be displayed in this format")

    def _display_financial_data(self, financial_data: Dict[str, Any]):
        """Display financial data"""
        if not financial_data:
            st.info("No financial data available")
            return
        
       
        summary_stats = financial_data.get("summary_stats", {})
        if summary_stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Profit", f"${summary_stats.get('total_profit', 0):,.2f}")
            with col2:
                st.metric("Total Sales", f"${summary_stats.get('total_gross_sales', 0):,.2f}")
            with col3:
                st.metric("Total Units", f"{summary_stats.get('total_units_sold', 0):,.0f}")
            with col4:
                st.metric("Data Points", f"{financial_data.get('data_points', 0):,}")
        
       
        raw_data = financial_data.get("raw_data", [])
        if raw_data:
            st.subheader("📋 Data Preview")
            df = pd.DataFrame(raw_data)
            st.dataframe(df.head(10), use_container_width=True)
            
            if len(df) > 10:
                st.info(f"Showing first 10 rows of {len(df)} total records")

    def _display_execution_status(self, result: Dict[str, Any]):
        """Display execution status"""
        st.subheader("🤖 Execution Status")
        
        successful_agents = result.get("successful_agents", [])
        failed_agents = result.get("failed_agents", [])
        metadata = result.get("metadata", {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Agents", metadata.get("total_agents", 0))
        with col2:
            st.metric("Successful", metadata.get("successful_agents", 0))
        with col3:
            st.metric("Failed", metadata.get("failed_agents", 0))
        
        # Agent details
        if successful_agents:
            st.success(f"✅ Successful agents: {', '.join(successful_agents)}")
        
        if failed_agents:
            st.error(f"❌ Failed agents: {', '.join(failed_agents)}")
        
        # Agent status details
        agent_status = result.get("agent_status", {})
        if agent_status:
            st.subheader("Agent Status Details")
            for agent_id, status in agent_status.items():
                st.write(f"**{agent_id.replace('_', ' ').title()}:** {status}")

def main():
    """Main function to run the Streamlit app"""
    ui = StreamlitUI()
    ui.run()

if __name__ == "__main__":
    main()
