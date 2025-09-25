import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL

from agents import (
    BaseAgent, AgentStatus, AgentResult,
    DataFetcherAgent, AnalyzerAgent, VisualizerAgent, SummarizerAgent
)

class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING_FOR_CLARIFICATION = "waiting_for_clarification"

@dataclass
class TaskPlan:
    task: str
    agents_needed: List[str]
    execution_order: List[str]
    context: Dict[str, Any]
    clarification_needed: bool = False
    clarification_questions: List[str] = None

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.status = TaskStatus.PENDING
        self.current_task = None
        self.execution_results: Dict[str, AgentResult] = {}
        self.logger = logging.getLogger("Orchestrator")
        
        # Initialize agents
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all available agents"""
        self.agents = {
            "data_fetcher": DataFetcherAgent(),
            "analyzer": AnalyzerAgent(),
            "visualizer": VisualizerAgent(),
            "summarizer": SummarizerAgent()
        }
        self.logger.info(f"Initialized {len(self.agents)} agents")
    
    async def process_request(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Main entry point for processing user requests"""
        try:
            self.status = TaskStatus.PLANNING
            self.current_task = user_request
            
            # Step 1: Plan the task
            task_plan = await self._plan_task(user_request, context or {})
            
            if task_plan.clarification_needed:
                self.status = TaskStatus.WAITING_FOR_CLARIFICATION
                return {
                    "status": "clarification_needed",
                    "questions": task_plan.clarification_questions,
                    "task": user_request
                }
            
            # Step 2: Execute the plan
            self.status = TaskStatus.EXECUTING
            execution_results = await self._execute_plan(task_plan)
            
            # Step 3: Aggregate results
            final_result = await self._aggregate_results(execution_results, task_plan)
            
            self.status = TaskStatus.COMPLETED
            return final_result
            
        except Exception as e:
            self.logger.error(f"Error processing request: {str(e)}")
            self.status = TaskStatus.ERROR
            return {
                "status": "error",
                "error": str(e),
                "task": user_request
            }
    
    async def _plan_task(self, task: str, context: Dict[str, Any]) -> TaskPlan:
        """Use LLM to plan which agents are needed and in what order"""
        try:
            # Get available agents and their capabilities
            agent_capabilities = self._get_agent_capabilities()
            
            # Create planning prompt
            planning_prompt = self._create_planning_prompt(task, agent_capabilities, context)
            
            # Call ChatGPT-4 for planning
            plan_response = await self._call_llm_for_planning(planning_prompt)
            
            # Parse the response to create task plan
            task_plan = self._parse_planning_response(task, plan_response, context)
            
            return task_plan
            
        except Exception as e:
            self.logger.error(f"Error in task planning: {str(e)}")
            # Fallback to basic planning
            return self._create_fallback_plan(task, context)
    
    def _get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all available agents"""
        capabilities = {}
        for agent_id, agent in self.agents.items():
            capabilities[agent_id] = agent.get_capabilities()
        return capabilities
    
    def _create_planning_prompt(self, task: str, agent_capabilities: Dict, context: Dict) -> str:
        """Create prompt for task planning"""
        prompt = f"""
        You are a task orchestrator for a multi-agent financial analysis system. 
        Analyze the user's request and determine which agents should be used and in what order.
        
        User Request: "{task}"
        
        Available Agents and Capabilities:
        """
        
        for agent_id, capabilities in agent_capabilities.items():
            prompt += f"\n- {agent_id}: {', '.join(capabilities)}"
        
        prompt += f"""
        
        Context: {context}
        
        IMPORTANT: If clarification_answers are provided in the context, use them to understand what the user wants and DO NOT ask for clarification again.
        
        CLARIFICATION RULES:
        - Ask for clarification if the request is vague or ambiguous (e.g., "analyze data", "show trends", "help me")
        - Ask for clarification if time period is not specified (e.g., "analyze profit" should ask "What time period?")
        - Ask for clarification if scope is unclear (e.g., "compare performance" should ask "Compare what?")
        - Ask for clarification if output format is not specified (e.g., "show me data" should ask "Do you want charts, tables, or reports?")
        
        Please respond with a JSON object containing:
        1. "agents_needed": List of agent IDs that should be used
        2. "execution_order": List of agent IDs in execution order
        3. "clarification_needed": Boolean indicating if clarification is needed (should be false if clarification_answers exist)
        4. "clarification_questions": List of questions if clarification is needed
        5. "reasoning": Brief explanation of the plan
        
        Example response for ambiguous request:
        {{
            "agents_needed": [],
            "execution_order": [],
            "clarification_needed": true,
            "clarification_questions": ["What specific data would you like me to analyze?", "What time period are you interested in?", "What type of analysis do you need?"],
            "reasoning": "Request is too vague, need clarification on scope and requirements"
        }}
        
        Example response for clear request:
        {{
            "agents_needed": ["data_fetcher", "analyzer", "visualizer", "summarizer"],
            "execution_order": ["data_fetcher", "analyzer", "visualizer", "summarizer"],
            "clarification_needed": false,
            "clarification_questions": [],
            "reasoning": "Need to fetch data, analyze it, create visualizations, and summarize results"
        }}
        """
        
        return prompt
    
    async def _call_llm_for_planning(self, prompt: str) -> str:
        """Call ChatGPT-4 for task planning"""
        try:
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            
            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a task orchestrator. Always respond with valid JSON. Be precise and logical in your planning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"Error calling LLM for planning: {str(e)}")
            raise
    
    def _parse_planning_response(self, task: str, response: str, context: Dict) -> TaskPlan:
        """Parse LLM response to create task plan"""
        import json
        
        try:
            
            response_clean = response.strip()
            if response_clean.startswith("```json"):
                response_clean = response_clean[7:-3]
            elif response_clean.startswith("```"):
                response_clean = response_clean[3:-3]
            
            plan_data = json.loads(response_clean)
            
            return TaskPlan(
                task=task,
                agents_needed=plan_data.get("agents_needed", []),
                execution_order=plan_data.get("execution_order", []),
                context=context,
                clarification_needed=plan_data.get("clarification_needed", False),
                clarification_questions=plan_data.get("clarification_questions", [])
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Error parsing planning response: {str(e)}")
            
            return self._create_fallback_plan(task, context)
    
    def _create_fallback_plan(self, task: str, context: Dict) -> TaskPlan:
        """Create a basic fallback plan when LLM planning fails"""
        
        default_order = ["data_fetcher", "analyzer", "visualizer", "summarizer"]
        
        
        clarification_needed = not bool(context.get("clarification_answers"))
        
        
        if clarification_needed:
            
            task_lower = task.lower()
            vague_phrases = [
                "help me", "what should i do", "i need information", "can you help",
                "tell me something", "what's going on", "i want to know", "show me something",
                "give me data", "i need help", "analyze data", "show trends", "compare performance",
                "show me", "give me", "tell me", "what is", "how do", "can you"
            ]
            
           
            is_vague = any(phrase in task_lower for phrase in vague_phrases) or len(task.split()) <= 3
            
            if is_vague:
                clarification_questions = [
                    "What specific financial data would you like me to analyze?",
                    "What time period are you interested in? (e.g., last quarter, last year)",
                    "What type of analysis do you need? (e.g., trends, comparisons, summaries)",
                    "Do you want charts, tables, or reports?"
                ]
                
                return TaskPlan(
                    task=task,
                    agents_needed=[],
                    execution_order=[],
                    context=context,
                    clarification_needed=True,
                    clarification_questions=clarification_questions
                )
        
        
        agents_needed = []
        task_lower = task.lower()
        
        if any(word in task_lower for word in ["fetch", "get", "data", "download"]):
            agents_needed.append("data_fetcher")
        
        if any(word in task_lower for word in ["analyze", "analysis", "trend", "calculate"]):
            agents_needed.append("analyzer")
        
        if any(word in task_lower for word in ["chart", "graph", "plot", "visualize"]):
            agents_needed.append("visualizer")
        
        if any(word in task_lower for word in ["summarize", "summary", "report", "conclusion"]):
            agents_needed.append("summarizer")
        
        
        if not agents_needed:
            agents_needed = default_order
        
        return TaskPlan(
            task=task,
            agents_needed=agents_needed,
            execution_order=agents_needed,
            context=context,
            clarification_needed=False
        )
    
    async def _execute_plan(self, task_plan: TaskPlan) -> Dict[str, AgentResult]:
        """Execute the planned tasks in order"""
        execution_results = {}
        shared_context = task_plan.context.copy()
        
        for agent_id in task_plan.execution_order:
            if agent_id not in self.agents:
                self.logger.warning(f"Agent {agent_id} not found, skipping")
                continue
            
            agent = self.agents[agent_id]
            
            try:
                self.logger.info(f"Executing agent: {agent_id}")
                
                
                result = await agent.execute(task_plan.task, shared_context)
                execution_results[agent_id] = result
                
                
                shared_context.update(agent.context)
                
                
                if result.status == AgentStatus.ERROR:
                    self.logger.error(f"Agent {agent_id} failed: {result.error}")
                
            except Exception as e:
                self.logger.error(f"Error executing agent {agent_id}: {str(e)}")
                execution_results[agent_id] = AgentResult(
                    agent_id=agent_id,
                    status=AgentStatus.ERROR,
                    data=None,
                    error=str(e)
                )
        
        return execution_results
    
    async def _aggregate_results(self, execution_results: Dict[str, AgentResult], task_plan: TaskPlan) -> Dict[str, Any]:
        """Aggregate results from all agents into final response"""
        successful_results = {k: v for k, v in execution_results.items() if v.status == AgentStatus.COMPLETED}
        failed_results = {k: v for k, v in execution_results.items() if v.status == AgentStatus.ERROR}
        
        
        aggregated_data = {}
        for agent_id, result in successful_results.items():
            if result.data:
                aggregated_data[agent_id] = result.data
        
        
        summary = None
        if "summarizer" in successful_results and successful_results["summarizer"].data:
            summary = successful_results["summarizer"].data
        
        
        visualizations = {}
        if "visualizer" in successful_results and successful_results["visualizer"].data:
            visualizations = successful_results["visualizer"].data
        
        
        analysis = {}
        if "analyzer" in successful_results and successful_results["analyzer"].data:
            analysis = successful_results["analyzer"].data
        
        
        financial_data = {}
        if "data_fetcher" in successful_results and successful_results["data_fetcher"].data:
            financial_data = successful_results["data_fetcher"].data
        
        return {
            "status": "completed",
            "task": task_plan.task,
            "summary": summary,
            "analysis": analysis,
            "visualizations": visualizations,
            "financial_data": financial_data,
            "successful_agents": list(successful_results.keys()),
            "failed_agents": list(failed_results.keys()),
            "agent_status": {agent_id: result.status.value for agent_id, result in execution_results.items()},
            "metadata": {
                "total_agents": len(execution_results),
                "successful_agents": len(successful_results),
                "failed_agents": len(failed_results)
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status"""
        return {
            "status": self.status.value,
            "current_task": self.current_task,
            "available_agents": list(self.agents.keys()),
            "agent_status": {agent_id: agent.status.value for agent_id, agent in self.agents.items()}
        }
    
    async def handle_clarification(self, clarification_answers: Dict[str, str]) -> Dict[str, Any]:
        """Handle user clarification responses"""
        if self.status != TaskStatus.WAITING_FOR_CLARIFICATION:
            return {"error": "No clarification needed at this time"}
        
        
        updated_context = {"clarification_answers": clarification_answers}
        
        
        self.status = TaskStatus.PLANNING
        
        
        return await self.process_request(self.current_task, updated_context)
