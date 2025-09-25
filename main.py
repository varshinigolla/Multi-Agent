import asyncio
import logging
import json
from typing import Dict, Any
from orchestrator import MultiAgentOrchestrator, TaskStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class MultiAgentTaskSolver:
    def __init__(self):
        self.orchestrator = MultiAgentOrchestrator()
        self.logger = logging.getLogger("TaskSolver")
        
    async def run_interactive_mode(self):
        """Run the interactive command-line interface"""
        print("Multi-Agent Financial Analysis System")
        print("=" * 50)
        print("Enter your financial analysis requests in plain language.")
        print("Type 'quit' or 'exit' to stop.")
        print("Type 'status' to see current system status.")
        print("Type 'help' for available commands.")
        print()
        
        while True:
            try:
                user_input = input("\n Your request: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break
                elif user_input.lower() == 'status':
                    self._show_status()
                    continue
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # Process the request
                await self._process_user_request(user_input)
                
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                self.logger.error(f"Error in interactive mode: {str(e)}")
                print(f"Error: {str(e)}")
    
    async def _process_user_request(self, request: str):
        """Process a single user request"""
        print(f"\nProcessing: {request}")
        print("Planning and executing...")
        
        try:
            # Process the request
            result = await self.orchestrator.process_request(request)
            
            # Handle different result types
            if result.get("status") == "clarification_needed":
                await self._handle_clarification(result)
            elif result.get("status") == "completed":
                self._display_results(result)
            elif result.get("status") == "error":
                print(f"Error: {result.get('error', 'Unknown error')}")
            else:
                print(f"Unexpected result status: {result.get('status')}")
                
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            print(f"Error processing request: {str(e)}")
    
    async def _handle_clarification(self, result: Dict[str, Any]):
        """Handle clarification requests from the orchestrator"""
        print("\nClarification needed:")
        questions = result.get("questions", [])
        
        for i, question in enumerate(questions, 1):
            print(f"{i}. {question}")
        
        print("\nPlease provide answers:")
        clarification_answers = {}
        
        for i, question in enumerate(questions, 1):
            answer = input(f"Answer {i}: ").strip()
            clarification_answers[f"question_{i}"] = answer
        
        print("\n🔄 Processing with clarification...")
        
        # Send clarification back to orchestrator
        updated_result = await self.orchestrator.handle_clarification(clarification_answers)
        
        if updated_result.get("status") == "completed":
            self._display_results(updated_result)
        elif updated_result.get("status") == "error":
            print(f"Error after clarification: {updated_result.get('error', 'Unknown error')}")
        else:
            print(f"Unexpected status after clarification: {updated_result.get('status')}")
            print(f"Response: {updated_result}")
    
    def _display_results(self, result: Dict[str, Any]):
        """Display the results in a formatted way"""
        print("\n" + "="*60)
        print("📊 ANALYSIS RESULTS")
        print("="*60)
        
        # Display summary if available
        if result.get("summary"):
            print("\n📋 SUMMARY:")
            print("-" * 30)
            print(result["summary"])
        
        # Display analysis if available
        if result.get("analysis"):
            print("\n📈 ANALYSIS:")
            print("-" * 30)
            self._display_analysis(result["analysis"])
        
        # Display financial data summary if available
        if result.get("financial_data"):
            print("\n💰 FINANCIAL DATA:")
            print("-" * 30)
            self._display_financial_data(result["financial_data"])
        
        # Display visualizations info
        if result.get("visualizations"):
            print("\n📊 VISUALIZATIONS:")
            print("-" * 30)
            for viz_name, viz_data in result["visualizations"].items():
                print(f"• {viz_data.get('title', viz_name)}")
        
        # Display execution status
        print("\n🤖 EXECUTION STATUS:")
        print("-" * 30)
        successful = result.get("successful_agents", [])
        failed = result.get("failed_agents", [])
        
        if successful:
            print(f"✅ Successful agents: {', '.join(successful)}")
        if failed:
            print(f"❌ Failed agents: {', '.join(failed)}")
        
        metadata = result.get("metadata", {})
        print(f"📊 Total agents: {metadata.get('total_agents', 0)}")
        print(f"✅ Successful: {metadata.get('successful_agents', 0)}")
        print(f"❌ Failed: {metadata.get('failed_agents', 0)}")
        
        print("\n" + "="*60)
    
    def _display_analysis(self, analysis: Dict[str, Any]):
        """Display analysis results in a readable format"""
        for key, value in analysis.items():
            # Handle different types of values
            if isinstance(value, dict):
                print(f"\n{str(key).replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)):
                        print(f"  {str(sub_key).replace('_', ' ').title()}: {sub_value}")
                    else:
                        print(f"  {str(sub_key).replace('_', ' ').title()}: {sub_value}")
            elif isinstance(value, (int, float)):
                print(f"{str(key).replace('_', ' ').title()}: {value}")
            elif isinstance(value, (list, tuple)):
                # Handle lists and tuples
                if len(value) > 0 and isinstance(value[0], tuple):
                    # Handle nested tuples (like from pandas groupby)
                    print(f"{str(key).replace('_', ' ').title()}:")
                    for item in value[:5]:  # Show first 5 items
                        print(f"  {item}")
                    if len(value) > 5:
                        print(f"  ... and {len(value) - 5} more")
                else:
                    print(f"{str(key).replace('_', ' ').title()}: {value}")
            else:
                print(f"{str(key).replace('_', ' ').title()}: {value}")
    
    def _display_financial_data(self, financial_data: Dict[str, Any]):
        """Display financial data summary"""
        data_points = financial_data.get("data_points", 0)
        date_range = financial_data.get("date_range", {})
        summary_stats = financial_data.get("summary_stats", {})
        
        print(f"Data Points: {data_points}")
        print(f"Date Range: {date_range.get('start', 'N/A')} to {date_range.get('end', 'N/A')}")
        
        if summary_stats:
            if "total_profit" in summary_stats:
                print(f"Total Profit: ${summary_stats['total_profit']:,.2f}")
            if "total_gross_sales" in summary_stats:
                print(f"Total Sales: ${summary_stats['total_gross_sales']:,.2f}")
            if "total_units_sold" in summary_stats:
                print(f"Total Units Sold: {summary_stats['total_units_sold']:,.0f}")
            
            if "segment_breakdown" in summary_stats:
                print(f"Segments: {', '.join(summary_stats['segment_breakdown'].keys())}")
            if "country_breakdown" in summary_stats:
                print(f"Countries: {', '.join(summary_stats['country_breakdown'].keys())}")
    
    def _show_status(self):
        """Show current system status"""
        status = self.orchestrator.get_status()
        print("\n📊 SYSTEM STATUS")
        print("-" * 20)
        print(f"Status: {status['status']}")
        print(f"Current Task: {status.get('current_task', 'None')}")
        print(f"Available Agents: {', '.join(status['available_agents'])}")
        
        print("\nAgent Status:")
        for agent_id, agent_status in status['agent_status'].items():
            status_emoji = "✅" if agent_status == "completed" else "⏳" if agent_status == "working" else "❌" if agent_status == "error" else "⭕"
            print(f"  {status_emoji} {agent_id}: {agent_status}")
    
    def _show_help(self):
        """Show help information"""
        print("\n📚 HELP - Available Commands")
        print("-" * 30)
        print("• Enter any financial analysis request in plain language")
        print("• Examples:")
        print("  - 'Analyze AAPL stock performance for the last 3 quarters'")
        print("  - 'Create a chart showing Microsoft stock trends'")
        print("  - 'Summarize Tesla's financial data and create visualizations'")
        print("  - 'Get Apple's quarterly performance and analyze trends'")
        print()
        print("• Commands:")
        print("  - 'status': Show current system status")
        print("  - 'help': Show this help message")
        print("  - 'quit' or 'exit': Exit the program")
        print()
        print("• The system will automatically:")
        print("  - Fetch financial data from Yahoo Finance")
        print("  - Analyze trends and performance")
        print("  - Create visualizations")
        print("  - Generate comprehensive summaries")

async def main():
    """Main entry point"""
    try:
       
        from config import OPENAI_API_KEY
        if not OPENAI_API_KEY:
            print("❌ Error: OPENAI_API_KEY not found in environment variables")
            print("Please set your OpenAI API key in a .env file or environment variable")
            return
        
        
        task_solver = MultiAgentTaskSolver()
        await task_solver.run_interactive_mode()
        
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        logging.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
