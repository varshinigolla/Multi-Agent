import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentStatus, AgentResult
import logging

class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="analyzer",
            role="Financial Analyzer",
            description="Analyzes financial data and identifies trends, patterns, and insights"
        )
        
    def can_handle(self, task: str) -> bool:
        """Check if task involves analysis"""
        keywords = ["analyze", "analysis", "trend", "pattern", "insight", "calculate", "compare", "performance"]
        return any(keyword in task.lower() for keyword in keywords)
        
    def get_capabilities(self) -> List[str]:
        return [
            "Calculate financial metrics",
            "Identify trends and patterns",
            "Compare performance across periods",
            "Generate statistical insights",
            "Analyze volatility and risk"
        ]
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Analyze financial data and extract insights"""
        try:
            self.update_status(AgentStatus.WORKING)
            financial_data = self.get_from_context("financial_data")
            if not financial_data and context:
                financial_data = context.get("financial_data")
            
            if not financial_data:
                raise ValueError("No financial data available for analysis")
 
            df = pd.DataFrame(financial_data["raw_data"])
            if df.empty:
                raise ValueError("No data available for analysis")

            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
       
            analysis_results = {}
            
            if "trend" in task.lower():
                analysis_results.update(self._analyze_trends(df))
            
            if "quarter" in task.lower():
                analysis_results.update(self._analyze_quarters(df))
            
            if "performance" in task.lower() or "profit" in task.lower():
                analysis_results.update(self._analyze_performance(df))
            
            if "segment" in task.lower():
                analysis_results.update(self._analyze_segments(df))
            
            if "country" in task.lower():
                analysis_results.update(self._analyze_countries(df))
            
            if "product" in task.lower():
                analysis_results.update(self._analyze_products(df))
            
  
            analysis_results.update(self._calculate_basic_metrics(df))
            
      
            self.add_to_context("analysis_results", analysis_results)
            
            self.update_status(AgentStatus.COMPLETED)
            self.store_result(analysis_results)
            
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data=analysis_results,
                metadata={"metrics_calculated": len(analysis_results)}
            )
            
        except Exception as e:
            self.logger.error(f"Error in analysis: {str(e)}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                data=None,
                error=str(e)
            )
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze profit and sales trends"""
        if 'Profit' not in df.columns:
            return {}
        
     
        if 'Date' in df.columns:
            daily_profit = df.groupby('Date')['Profit'].sum().sort_index()
            
         
            if len(daily_profit) >= 2:
                recent_trend = "upward" if daily_profit.iloc[-1] > daily_profit.iloc[0] else "downward"
                profit_change = ((daily_profit.iloc[-1] - daily_profit.iloc[0]) / abs(daily_profit.iloc[0])) * 100 if daily_profit.iloc[0] != 0 else 0
            else:
                recent_trend = "stable"
                profit_change = 0
        else:
           
            profit_values = df['Profit'].values
            if len(profit_values) >= 2:
               
                recent_trend = "upward" if profit_values[-1] > profit_values[0] else "downward"
                profit_change = ((profit_values[-1] - profit_values[0]) / abs(profit_values[0])) * 100 if profit_values[0] != 0 else 0
            else:
                recent_trend = "stable"
                profit_change = 0
        
        return {
            "trend_direction": recent_trend,
            "profit_change_percent": round(profit_change, 2),
            "total_profit": df['Profit'].sum(),
            "avg_daily_profit": df['Profit'].mean()
        }
    
    def _analyze_quarters(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze quarterly performance"""
        if 'Date' not in df.columns or 'Profit' not in df.columns:
            return {}
        
      
        df_with_date = df.copy()
        df_with_date['Date'] = pd.to_datetime(df_with_date['Date'])
        df_with_date.set_index('Date', inplace=True)
        
       
        quarterly_data = df_with_date.resample('Q').agg({
            'Profit': 'sum',
            'Gross Sales': 'sum',
            'Units Sold': 'sum',
            'COGS': 'sum'
        }).dropna()
        
        if len(quarterly_data) < 2:
            return {"quarterly_analysis": "Insufficient data for quarterly analysis"}
        
      
        quarterly_profit_changes = quarterly_data['Profit'].pct_change().dropna() * 100
        
      
        last_quarters = quarterly_profit_changes.tail(3)
        
        return {
            "quarterly_profit": quarterly_data['Profit'].to_dict(),
            "quarterly_profit_changes": quarterly_profit_changes.to_dict(),
            "last_3_quarters_avg_change": round(last_quarters.mean(), 2),
            "quarterly_volatility": round(quarterly_profit_changes.std(), 2),
            "best_quarter": round(quarterly_profit_changes.max(), 2),
            "worst_quarter": round(quarterly_profit_changes.min(), 2)
        }
    
    def _analyze_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze overall performance metrics"""
        if 'Profit' not in df.columns:
            return {}
        
       
        total_profit = df['Profit'].sum()
        avg_profit = df['Profit'].mean()
        profit_std = df['Profit'].std()
        
      
        profit_margin = 0
        if 'Gross Sales' in df.columns and df['Gross Sales'].sum() > 0:
            profit_margin = (total_profit / df['Gross Sales'].sum()) * 100
        
       
        efficiency_metrics = {}
        if 'Units Sold' in df.columns and 'Units Sold' in df.columns:
            efficiency_metrics['profit_per_unit'] = total_profit / df['Units Sold'].sum() if df['Units Sold'].sum() > 0 else 0
        
        return {
            "total_profit": round(total_profit, 2),
            "avg_profit": round(avg_profit, 2),
            "profit_std": round(profit_std, 2),
            "profit_margin_percent": round(profit_margin, 2),
            **efficiency_metrics
        }
    
    def _analyze_segments(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by segment"""
        if 'Segment' not in df.columns or 'Profit' not in df.columns:
            return {}
        
        segment_analysis = df.groupby('Segment').agg({
            'Profit': ['sum', 'mean', 'count'],
            'Gross Sales': 'sum',
            'Units Sold': 'sum'
        }).round(2)
        
       
        segment_analysis['Profit_Margin'] = (segment_analysis[('Profit', 'sum')] / segment_analysis[('Gross Sales', 'sum')] * 100).round(2)
        
        return {
            "segment_performance": segment_analysis.to_dict(),
            "best_segment": segment_analysis[('Profit', 'sum')].idxmax(),
            "worst_segment": segment_analysis[('Profit', 'sum')].idxmin()
        }
    
    def _analyze_countries(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by country"""
        if 'Country' not in df.columns or 'Profit' not in df.columns:
            return {}
        
        country_analysis = df.groupby('Country').agg({
            'Profit': ['sum', 'mean', 'count'],
            'Gross Sales': 'sum',
            'Units Sold': 'sum'
        }).round(2)
        
      
        country_analysis['Profit_Margin'] = (country_analysis[('Profit', 'sum')] / country_analysis[('Gross Sales', 'sum')] * 100).round(2)
        
        return {
            "country_performance": country_analysis.to_dict(),
            "best_country": country_analysis[('Profit', 'sum')].idxmax(),
            "worst_country": country_analysis[('Profit', 'sum')].idxmin()
        }
    
    def _analyze_products(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance by product"""
        if 'Product' not in df.columns or 'Profit' not in df.columns:
            return {}
        
        product_analysis = df.groupby('Product').agg({
            'Profit': ['sum', 'mean', 'count'],
            'Gross Sales': 'sum',
            'Units Sold': 'sum'
        }).round(2)
        
     
        product_analysis['Profit_Margin'] = (product_analysis[('Profit', 'sum')] / product_analysis[('Gross Sales', 'sum')] * 100).round(2)
        
        return {
            "product_performance": product_analysis.to_dict(),
            "best_product": product_analysis[('Profit', 'sum')].idxmax(),
            "worst_product": product_analysis[('Profit', 'sum')].idxmin()
        }
    
    def _calculate_basic_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate basic financial metrics"""
        metrics = {}
        
        if 'Profit' in df.columns:
            profit = df['Profit']
            metrics.update({
                "total_profit": round(profit.sum(), 2),
                "max_profit": round(profit.max(), 2),
                "min_profit": round(profit.min(), 2),
                "avg_profit": round(profit.mean(), 2)
            })
        
        if 'Gross Sales' in df.columns:
            sales = df['Gross Sales']
            metrics.update({
                "total_sales": round(sales.sum(), 2),
                "avg_sales": round(sales.mean(), 2)
            })
        
        if 'Units Sold' in df.columns:
            units = df['Units Sold']
            metrics.update({
                "total_units": round(units.sum(), 0),
                "avg_units": round(units.mean(), 2)
            })
        
        if 'COGS' in df.columns:
            cogs = df['COGS']
            metrics.update({
                "total_cogs": round(cogs.sum(), 2),
                "avg_cogs": round(cogs.mean(), 2)
            })
        
        return metrics
    
