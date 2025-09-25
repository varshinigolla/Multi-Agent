import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentStatus, AgentResult
import logging
import io
import base64

class VisualizerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="visualizer",
            role="Data Visualizer",
            description="Creates charts and visualizations from financial data"
        )
        
    def can_handle(self, task: str) -> bool:
        """Check if task involves visualization"""
        keywords = ["chart", "graph", "plot", "visualize", "visualization", "trend", "show"]
        return any(keyword in task.lower() for keyword in keywords)
        
    def get_capabilities(self) -> List[str]:
        return [
            "Create price charts",
            "Generate trend visualizations",
            "Plot quarterly comparisons",
            "Create volume charts",
            "Generate performance dashboards"
        ]
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Create visualizations based on task requirements"""
        try:
            self.update_status(AgentStatus.WORKING)
            
            # Get data from context (try both shared context and agent context)
            financial_data = self.get_from_context("financial_data")
            analysis_results = self.get_from_context("analysis_results")
            
            if not financial_data and context:
                financial_data = context.get("financial_data")
                analysis_results = context.get("analysis_results")
            
            if not financial_data:
                raise ValueError("No financial data available for visualization")
            
            # Convert to DataFrame
            hist_data = pd.DataFrame(financial_data["raw_data"])
            if hist_data.empty:
                raise ValueError("No data available for visualization")
            
            # Convert date column if it exists
            if 'Date' in hist_data.columns:
                hist_data['Date'] = pd.to_datetime(hist_data['Date'])
                hist_data.set_index('Date', inplace=True)
            # If no date column, just use the data as is
            
            # Create visualizations based on task
            visualizations = {}
            
            if "chart" in task.lower() or "plot" in task.lower():
                visualizations.update(self._create_price_chart(hist_data, task))
            
            if "quarter" in task.lower():
                visualizations.update(self._create_quarterly_chart(hist_data, task))
            
            if "volume" in task.lower():
                visualizations.update(self._create_volume_chart(hist_data, task))
            
            if "trend" in task.lower():
                visualizations.update(self._create_trend_chart(hist_data, analysis_results, task))
            
            # Always create a basic price chart if no specific chart requested
            if not visualizations:
                visualizations.update(self._create_price_chart(hist_data, task))
            
            # Store visualizations in context
            self.add_to_context("visualizations", visualizations)
            
            self.update_status(AgentStatus.COMPLETED)
            self.store_result(visualizations)
            
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data=visualizations,
                metadata={"charts_created": len(visualizations)}
            )
            
        except Exception as e:
            self.logger.error(f"Error creating visualizations: {str(e)}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                data=None,
                error=str(e)
            )
    
    def _create_price_chart(self, df: pd.DataFrame, task: str) -> Dict[str, Any]:
        """Create profit trend chart"""
        if 'Profit' not in df.columns:
            return {}
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Group by date to get daily profit totals
        if 'Date' in df.columns:
            daily_profit = df.groupby('Date')['Profit'].sum().sort_index()
            
            # Add profit line
            fig.add_trace(go.Scatter(
                x=daily_profit.index,
                y=daily_profit.values,
                mode='lines+markers',
                name='Daily Profit',
                line=dict(color='blue', width=2)
            ))
            
            # Add moving average if requested
            if "moving" in task.lower() or "average" in task.lower():
                ma_7 = daily_profit.rolling(window=7).mean()
                fig.add_trace(go.Scatter(
                    x=daily_profit.index,
                    y=ma_7.values,
                    mode='lines',
                    name='7-Day Average',
                    line=dict(color='orange', width=1, dash='dash')
                ))
            
            # Update layout
            fig.update_layout(
                title=f"Profit Trend Chart - {daily_profit.index[0].strftime('%Y-%m-%d')} to {daily_profit.index[-1].strftime('%Y-%m-%d')}",
                xaxis_title="Date",
                yaxis_title="Profit ($)",
                hovermode='x unified',
                template="plotly_white"
            )
        else:
            # Simple bar chart if no date column
            fig.add_trace(go.Bar(
                x=list(range(len(df))),
                y=df['Profit'],
                name='Profit',
                marker_color='blue'
            ))
            
            fig.update_layout(
                title="Profit Chart",
                xaxis_title="Record",
                yaxis_title="Profit ($)",
                template="plotly_white"
            )
        
        # Convert to base64 for storage
        chart_html = fig.to_html(include_plotlyjs='cdn')
        chart_base64 = base64.b64encode(chart_html.encode()).decode()
        
        return {
            "profit_chart": {
                "type": "plotly",
                "data": chart_base64,
                "title": "Profit Trend Chart"
            }
        }
    
    def _create_quarterly_chart(self, df: pd.DataFrame, task: str) -> Dict[str, Any]:
        """Create quarterly performance chart"""
        if 'Profit' not in df.columns or 'Date' not in df.columns:
            return {}
        
        # Set date as index and group by quarters
        df_with_date = df.copy()
        df_with_date['Date'] = pd.to_datetime(df_with_date['Date'])
        df_with_date.set_index('Date', inplace=True)
        
        # Group by quarters
        quarterly_data = df_with_date.resample('Q').agg({
            'Profit': 'sum',
            'Gross Sales': 'sum',
            'Units Sold': 'sum'
        }).dropna()
        
        if len(quarterly_data) < 2:
            return {"quarterly_chart": "Insufficient data for quarterly chart"}
        
        # Calculate quarterly profit changes
        quarterly_profit_changes = quarterly_data['Profit'].pct_change().dropna() * 100
        
        # Create bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=[q.strftime('%Y-Q%q') for q in quarterly_profit_changes.index],
            y=quarterly_profit_changes.values,
            name='Quarterly Profit Change (%)',
            marker_color=['green' if x > 0 else 'red' for x in quarterly_profit_changes.values]
        ))
        
        fig.update_layout(
            title="Quarterly Profit Changes",
            xaxis_title="Quarter",
            yaxis_title="Profit Change (%)",
            template="plotly_white"
        )
        
        chart_html = fig.to_html(include_plotlyjs='cdn')
        chart_base64 = base64.b64encode(chart_html.encode()).decode()
        
        return {
            "quarterly_chart": {
                "type": "plotly",
                "data": chart_base64,
                "title": "Quarterly Profit Changes"
            }
        }
    
    def _create_volume_chart(self, df: pd.DataFrame, task: str) -> Dict[str, Any]:
        """Create units sold chart"""
        if 'Units Sold' not in df.columns:
            return {}
        
        # Create subplot with profit and units sold
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Profit', 'Units Sold'),
            row_heights=[0.7, 0.3]
        )
        
        # Profit chart
        if 'Date' in df.columns:
            daily_profit = df.groupby('Date')['Profit'].sum().sort_index()
            fig.add_trace(go.Scatter(
                x=daily_profit.index,
                y=daily_profit.values,
                mode='lines',
                name='Daily Profit',
                line=dict(color='blue')
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x=list(range(len(df))),
                y=df['Profit'],
                mode='lines',
                name='Profit',
                line=dict(color='blue')
            ), row=1, col=1)
        
        # Units sold chart
        if 'Date' in df.columns:
            daily_units = df.groupby('Date')['Units Sold'].sum().sort_index()
            fig.add_trace(go.Bar(
                x=daily_units.index,
                y=daily_units.values,
                name='Daily Units Sold',
                marker_color='lightblue'
            ), row=2, col=1)
        else:
            fig.add_trace(go.Bar(
                x=list(range(len(df))),
                y=df['Units Sold'],
                name='Units Sold',
                marker_color='lightblue'
            ), row=2, col=1)
        
        fig.update_layout(
            title="Profit and Units Sold Chart",
            template="plotly_white",
            height=600
        )
        
        chart_html = fig.to_html(include_plotlyjs='cdn')
        chart_base64 = base64.b64encode(chart_html.encode()).decode()
        
        return {
            "units_chart": {
                "type": "plotly",
                "data": chart_base64,
                "title": "Profit and Units Sold Chart"
            }
        }
    
    def _create_trend_chart(self, df: pd.DataFrame, analysis_results: Dict, task: str) -> Dict[str, Any]:
        """Create trend analysis chart"""
        if 'Profit' not in df.columns:
            return {}
        
        # Create profit trend chart
        fig = go.Figure()
        
        if 'Date' in df.columns:
            daily_profit = df.groupby('Date')['Profit'].sum().sort_index()
            
            # Add profit line
            fig.add_trace(go.Scatter(
                x=daily_profit.index,
                y=daily_profit.values,
                mode='lines+markers',
                name='Daily Profit',
                line=dict(color='blue', width=2)
            ))
            
            # Add trend line if we have moving averages
            if analysis_results.get('avg_daily_profit'):
                ma_7 = daily_profit.rolling(window=7).mean()
                fig.add_trace(go.Scatter(
                    x=daily_profit.index,
                    y=ma_7.values,
                    mode='lines',
                    name='7-Day Average',
                    line=dict(color='orange', dash='dash')
                ))
            
            fig.update_layout(
                title="Profit Trend Analysis",
                xaxis_title="Date",
                yaxis_title="Profit ($)",
                template="plotly_white"
            )
        else:
            # Simple bar chart if no date column
            fig.add_trace(go.Bar(
                x=list(range(len(df))),
                y=df['Profit'],
                name='Profit',
                marker_color='blue'
            ))
            
            fig.update_layout(
                title="Profit Trend Analysis",
                xaxis_title="Record",
                yaxis_title="Profit ($)",
                template="plotly_white"
            )
        
        chart_html = fig.to_html(include_plotlyjs='cdn')
        chart_base64 = base64.b64encode(chart_html.encode()).decode()
        
        return {
            "trend_chart": {
                "type": "plotly",
                "data": chart_base64,
                "title": "Profit Trend Analysis"
            }
        }
