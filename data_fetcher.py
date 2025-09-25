import pandas as pd
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, AgentStatus, AgentResult
import logging
import os

class DataFetcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            agent_id="data_fetcher",
            role="Data Fetcher",
            description="Fetches financial data from Excel file"
        )
        self.excel_file = "04-01-Financial Sample Data.xlsx"
        
    def can_handle(self, task: str) -> bool:
        """Check if task involves data fetching"""
        keywords = ["fetch", "get", "download", "data", "financial", "stock", "price", "quarter", "quarterly"]
        return any(keyword in task.lower() for keyword in keywords)
        
    def get_capabilities(self) -> List[str]:
        return [
            "Fetch financial sales data",
            "Get profit and revenue data",
            "Download quarterly/annual financial data",
            "Retrieve segment and country data",
            "Get product performance data"
        ]
        
    async def execute(self, task: str, context: Dict[str, Any] = None) -> AgentResult:
        """Fetch financial data from Excel file based on task requirements"""
        try:
            self.update_status(AgentStatus.WORKING)
         
            if not os.path.exists(self.excel_file):
                raise FileNotFoundError(f"Excel file {self.excel_file} not found")
            
            self.logger.info(f"Loading financial data from {self.excel_file}")
            df = pd.read_excel(self.excel_file)
            
         
            filters = self._extract_filters(task, context)
            
          
            filtered_df = self._apply_filters(df, filters)
            
          
            if 'Date' in filtered_df.columns:
                filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])
                filtered_df = filtered_df.sort_values('Date')
           
            
           
            result_data = {
                "raw_data": filtered_df.to_dict('records'),
                "summary_stats": self._calculate_summary_stats(filtered_df),
                "filters_applied": filters,
                "data_points": len(filtered_df),
                "columns": filtered_df.columns.tolist(),
                "date_range": self._get_date_range(filtered_df)
            }
            
         
            self.add_to_context("financial_data", result_data)
            self.add_to_context("dataframe", filtered_df)
            
            self.update_status(AgentStatus.COMPLETED)
            self.store_result(result_data, {"data_points": len(filtered_df)})
            
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.COMPLETED,
                data=result_data,
                metadata={"data_points": len(filtered_df)}
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {str(e)}")
            self.update_status(AgentStatus.ERROR)
            return AgentResult(
                agent_id=self.agent_id,
                status=AgentStatus.ERROR,
                data=None,
                error=str(e)
            )
    
    def _extract_filters(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract filters from task for Excel data"""
        filters = {}
        task_lower = task.lower()
        
       
        segments = ["government", "midmarket", "midmarkets", "channel partners", "enterprise", "small business"]
        for segment in segments:
            if segment in task_lower:
                filters["segment"] = segment.title()
                break
        
       
        countries = ["canada", "germany", "france", "mexico", "usa", "united states"]
        for country in countries:
            if country in task_lower:
                filters["country"] = country.title()
                break
        
       
        products = ["carretera", "montana", "paseo", "vente", "amarilla", "touring"]
        for product in products:
            if product in task_lower:
                filters["product"] = product.title()
                break
        
       
        if "last" in task_lower:
            if "3" in task_lower or "three" in task_lower:
                filters["quarters"] = 3
            elif "2" in task_lower or "two" in task_lower:
                filters["quarters"] = 2
            elif "1" in task_lower or "one" in task_lower:
                filters["quarters"] = 1
            elif "month" in task_lower:
                filters["months"] = 1
            elif "year" in task_lower:
                filters["years"] = 1
        
        return filters
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to the dataframe"""
        filtered_df = df.copy()
        
       
        if "segment" in filters:
            filtered_df = filtered_df[filtered_df["Segment"].str.contains(filters["segment"], case=False, na=False)]
        
       
        if "country" in filters:
            filtered_df = filtered_df[filtered_df["Country"].str.contains(filters["country"], case=False, na=False)]
        
       
        if "product" in filters:
            filtered_df = filtered_df[filtered_df["Product"].str.contains(filters["product"], case=False, na=False)]
        
       
        if "Date" in filtered_df.columns:
           
            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            
            if "quarters" in filters:
               
                quarters = filters["quarters"]
                latest_date = filtered_df["Date"].max()
                quarter_start = latest_date - pd.DateOffset(months=quarters * 3)
                filtered_df = filtered_df[filtered_df["Date"] >= quarter_start]
            elif "months" in filters:
               
                months = filters["months"]
                latest_date = filtered_df["Date"].max()
                month_start = latest_date - pd.DateOffset(months=months)
                filtered_df = filtered_df[filtered_df["Date"] >= month_start]
            elif "years" in filters:
               
                years = filters["years"]
                latest_date = filtered_df["Date"].max()
                year_start = latest_date - pd.DateOffset(years=years)
                filtered_df = filtered_df[filtered_df["Date"] >= year_start]
       
        
        return filtered_df
    
    def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate summary statistics for the filtered data"""
        stats = {}
        
      
        if "Profit" in df.columns:
            stats["total_profit"] = df["Profit"].sum()
            stats["avg_profit"] = df["Profit"].mean()
            stats["profit_std"] = df["Profit"].std()
        
        if "Gross Sales" in df.columns:
            stats["total_gross_sales"] = df["Gross Sales"].sum()
            stats["avg_gross_sales"] = df["Gross Sales"].mean()
        
        if "COGS" in df.columns:
            stats["total_cogs"] = df["COGS"].sum()
            stats["avg_cogs"] = df["COGS"].mean()
        
        if "Units Sold" in df.columns:
            stats["total_units_sold"] = df["Units Sold"].sum()
            stats["avg_units_sold"] = df["Units Sold"].mean()
        
       
        if "Date" in df.columns:
            stats["date_range"] = {
                "start": df["Date"].min().strftime("%Y-%m-%d"),
                "end": df["Date"].max().strftime("%Y-%m-%d")
            }
        else:
            stats["date_range"] = {"start": "N/A", "end": "N/A"}
        
      
        if "Segment" in df.columns:
            stats["segment_breakdown"] = df["Segment"].value_counts().to_dict()
        
      
        if "Country" in df.columns:
            stats["country_breakdown"] = df["Country"].value_counts().to_dict()
        
        return stats
    
    def _get_date_range(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get date range of the filtered data"""
        if "Date" in df.columns and not df.empty:
            return {
                "start": df["Date"].min().strftime("%Y-%m-%d"),
                "end": df["Date"].max().strftime("%Y-%m-%d")
            }
        return {"start": "N/A", "end": "N/A"}
