import openai
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentStatus, AgentResult
import logging
from config import OPENAI_API_KEY, OPENAI_MODEL
import os
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SummarizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="summarizer",
            role="Report Summarizer",
            description="Creates comprehensive summaries and reports from financial data and analysis"
        )
        
    def can_handle(self, task: str) -> bool:
        """Check if task involves summarization"""
        keywords = ["summarize", "summary", "report", "conclusion", "overview", "insights"]
        return any(keyword in task.lower() for keyword in keywords)
        
    def get_capabilities(self) -> List[str]:
        return [
            "Generate executive summaries",
            "Create financial reports",
            "Extract key insights",
            "Write trend analysis reports",
            "Provide investment recommendations"
        ]
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Generate comprehensive summary and report"""
        try:
            self.update_status(AgentStatus.WORKING)
            
            # Get data from context (try both shared context and agent context)
            financial_data = self.get_from_context("financial_data")
            analysis_results = self.get_from_context("analysis_results")
            visualizations = self.get_from_context("visualizations")
            
            if not financial_data and context:
                financial_data = context.get("financial_data")
                analysis_results = context.get("analysis_results")
                visualizations = context.get("visualizations")
            
            if not financial_data:
                raise ValueError("No financial data available for summarization")
            
            # Prepare data for LLM
            summary_data = self._prepare_summary_data(financial_data, analysis_results, visualizations)
            
            # Generate summary using ChatGPT-4
            summary = await self._generate_summary(task, summary_data)
            
            # Store summary in context
            self.add_to_context("summary", summary)
            
            self.update_status(AgentStatus.COMPLETED)
            self.store_result(summary)
            
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data=summary,
                metadata={"summary_length": len(summary)}
            )
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                data=None,
                error=str(e)
            )
    
    def _prepare_summary_data(self, financial_data: Dict, analysis_results: Dict, visualizations: Dict) -> Dict[str, Any]:
        """Prepare structured data for LLM summarization"""
        summary_data = {
            "symbol": financial_data.get("symbol", "Unknown"),
            "period": financial_data.get("period", "Unknown"),
            "data_points": financial_data.get("data_points", 0),
            "company_info": financial_data.get("company_info", {}),
            "analysis": analysis_results or {},
            "visualizations": list(visualizations.keys()) if visualizations else [],
            "has_financials": financial_data.get("financials") is not None
        }
        
        return summary_data
    
    async def _generate_summary(self, task: str, data: Dict[str, Any]) -> str:
        """Generate summary using ChatGPT-4"""
        try:
            # Initialize OpenAI client
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            # Create prompt for summarization
            prompt = self._create_summarization_prompt(task, data)
            
            # Call ChatGPT-4
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a financial analyst expert. Provide clear, accurate, and professional financial analysis summaries. Focus on key insights, trends, and actionable information."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error calling OpenAI API: {str(e)}")
            # Fallback to basic summary
            return self._create_fallback_summary(data)
    
    def _create_summarization_prompt(self, task: str, data: Dict[str, Any]) -> str:
        """Create detailed prompt for ChatGPT-4"""
        symbol = data.get("symbol", "Unknown")
        period = data.get("period", "Unknown")
        
        prompt = f"""
        Please analyze the following financial data and provide a comprehensive summary based on the user's request: "{task}"

        Financial Data Summary:
        - Symbol: {symbol}
        - Period: {period}
        - Data Points: {data.get("data_points", 0)}
        
        Company Information:
        {self._format_company_info(data.get("company_info", {}))}
        
        Analysis Results:
        {self._format_analysis_results(data.get("analysis", {}))}
        
        Available Visualizations: {', '.join(data.get("visualizations", []))}
        
        Please provide:
        1. Executive Summary (2-3 sentences)
        2. Key Financial Metrics and Trends
        3. Performance Analysis
        4. Risk Assessment (if applicable)
        5. Key Insights and Recommendations
        6. Conclusion
        
        Format the response in a professional, easy-to-read manner suitable for business stakeholders.
        """
        
        return prompt
    
    def _format_company_info(self, company_info: Dict) -> str:
        """Format company information for the prompt"""
        if not company_info:
            return "No company information available"
        
        key_info = []
        if company_info.get("longName"):
            key_info.append(f"Company: {company_info['longName']}")
        if company_info.get("sector"):
            key_info.append(f"Sector: {company_info['sector']}")
        if company_info.get("industry"):
            key_info.append(f"Industry: {company_info['industry']}")
        if company_info.get("marketCap"):
            key_info.append(f"Market Cap: ${company_info['marketCap']:,}")
        
        return "\n".join(key_info) if key_info else "Basic company information available"
    
    def _format_analysis_results(self, analysis: Dict) -> str:
        """Format analysis results for the prompt"""
        if not analysis:
            return "No analysis results available"
        
        formatted = []
        for key, value in analysis.items():
            if isinstance(value, (int, float)):
                formatted.append(f"{key.replace('_', ' ').title()}: {value}")
            elif isinstance(value, dict):
                formatted.append(f"{key.replace('_', ' ').title()}: {len(value)} items")
            else:
                formatted.append(f"{key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(formatted) if formatted else "Analysis results available"
    
    def _create_fallback_summary(self, data: Dict[str, Any]) -> str:
        """Create a basic summary when LLM is unavailable"""
        symbol = data.get("symbol", "Unknown")
        period = data.get("period", "Unknown")
        data_points = data.get("data_points", 0)
        
        summary = f"""
        Financial Analysis Summary for {symbol}
        =====================================
        
        Period Analyzed: {period}
        Data Points: {data_points}
        
        Analysis Results:
        {self._format_analysis_results(data.get("analysis", {}))}
        
        Note: This is a basic summary. For detailed analysis, please ensure the LLM service is available.
        """
        
        return summary
