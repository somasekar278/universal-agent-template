"""
Generic Learning Agents (Levels 1-5)

Example agents using domain-agnostic schemas for the learning path.
These can be adapted to any use case (customer support, analytics, etc.)

Prerequisites:
    pip install sota-agent-framework
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Add framework to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.base import Agent
from shared.schemas.learning import (
    # Level 1
    ChatInput,
    ChatOutput,
    # Level 2
    ContextAwareInput,
    ContextAwareOutput,
    # Level 3
    APIRequest,
    APIResponse,
    # Level 4
    WorkflowInput,
    WorkflowOutput,
    TaskStep,
    TaskStatus,
    # Level 5
    CollaborationRequest,
    CollaborationResponse,
)


# ============================================================================
# Level 1: Simple Chatbot Agent
# ============================================================================

class SimpleChatbotAgent(Agent):
    """
    Level 1: Simple chatbot agent using generic schemas.
    
    Can be adapted to any domain:
    - Customer support
    - FAQ bot
    - Technical assistant
    - General Q&A
    """
    
    async def process(self, request: ChatInput) -> ChatOutput:
        """Process chat input and return response."""
        
        question = request.question.lower()
        
        # Simple rule-based responses (replace with LLM in production)
        if "hello" in question or "hi" in question:
            answer = "Hello! How can I help you today?"
            confidence = 0.95
        elif "help" in question:
            answer = "I'm here to help! What do you need assistance with?"
            confidence = 0.90
        elif "?" in question:
            answer = f"That's a great question. Let me help you with that."
            confidence = 0.70
        else:
            answer = f"I understand you said: {request.question}. How can I assist?"
            confidence = 0.60
        
        return ChatOutput(
            answer=answer,
            confidence=confidence,
            sources=["rule_engine"],
            metadata={
                "user_id": request.user_id,
                "session_id": request.session_id,
                "processed_at": datetime.utcnow().isoformat()
            }
        )


# ============================================================================
# Level 2: Context-Aware Agent (with Memory)
# ============================================================================

class ContextAwareAgent(Agent):
    """
    Level 2: Context-aware agent that remembers conversations.
    
    Features:
    - Conversation history
    - Context retrieval
    - Memory storage
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory = {}  # Simple in-memory storage (use MemoryManager in production)
    
    async def process(self, request: ContextAwareInput) -> ContextAwareOutput:
        """Process with context awareness."""
        
        session_id = request.session_id
        
        # Retrieve context from memory
        context_used = []
        if request.retrieve_context and session_id in self.memory:
            context_used = self.memory[session_id][-request.max_context_items:]
        
        # Generate response (replace with LLM + context in production)
        if context_used:
            response = f"Based on our previous conversation about {', '.join(c['topic'] for c in context_used)}, "
            response += f"here's my answer to '{request.message}': [contextual response here]"
            confidence = 0.85
        else:
            response = f"Regarding '{request.message}': [response here]"
            confidence = 0.70
        
        # Store to memory
        if session_id not in self.memory:
            self.memory[session_id] = []
        
        self.memory[session_id].append({
            "message": request.message,
            "response": response,
            "topic": "general",  # Extract topic in production
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return ContextAwareOutput(
            response=response,
            confidence=confidence,
            context_used=[c["message"] for c in context_used],
            stored_to_memory=True,
            memory_summary=f"Stored interaction. Total items: {len(self.memory[session_id])}"
        )


# ============================================================================
# Level 3: Production API Agent
# ============================================================================

class ProductionAPIAgent(Agent):
    """
    Level 3: Production-ready API agent.
    
    Features:
    - Structured API requests
    - Health checks
    - Error handling
    - Monitoring
    """
    
    async def process(self, request: APIRequest) -> APIResponse:
        """Process API request."""
        
        start_time = datetime.utcnow()
        
        try:
            # Route to appropriate handler based on endpoint
            if request.endpoint == "analyze":
                result = await self._analyze(request.data)
            elif request.endpoint == "predict":
                result = await self._predict(request.data)
            elif request.endpoint == "classify":
                result = await self._classify(request.data)
            else:
                raise ValueError(f"Unknown endpoint: {request.endpoint}")
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return APIResponse(
                success=True,
                data=result,
                request_id=request.request_id,
                processing_time_ms=processing_time,
                metadata={
                    "endpoint": request.endpoint,
                    "user_id": request.user_id
                }
            )
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return APIResponse(
                success=False,
                data={},
                error=str(e),
                request_id=request.request_id,
                processing_time_ms=processing_time
            )
    
    async def _analyze(self, data: dict) -> dict:
        """Analyze data."""
        return {"analysis": "completed", "insights": ["insight_1", "insight_2"]}
    
    async def _predict(self, data: dict) -> dict:
        """Make prediction."""
        return {"prediction": 0.75, "confidence": 0.85}
    
    async def _classify(self, data: dict) -> dict:
        """Classify data."""
        return {"class": "category_A", "probability": 0.92}


# ============================================================================
# Level 4: Complex Workflow Agent (Plan-Act-Critique)
# ============================================================================

class WorkflowAgent(Agent):
    """
    Level 4: Complex workflow agent with Plan-Act-Critique loops.
    
    Features:
    - Task decomposition
    - Step-by-step execution
    - Self-critique
    - Re-planning
    """
    
    async def process(self, request: WorkflowInput) -> WorkflowOutput:
        """Execute complex workflow."""
        
        start_time = datetime.utcnow()
        iterations = 0
        optimizations_applied = []
        
        # Step 1: PLAN
        plan = await self._create_plan(request.objective, request.context)
        
        # Step 2: ACT (execute plan)
        execution_results = await self._execute_plan(plan)
        iterations += 1
        
        # Step 3: CRITIQUE (if required)
        critiques = []
        if request.require_critique:
            critiques = await self._critique_results(
                request.objective,
                execution_results
            )
            
            # Step 4: RE-PLAN if needed (and within iteration limit)
            while critiques and iterations < request.max_iterations:
                print(f"  🔄 Re-planning (iteration {iterations + 1})")
                plan = await self._replan(plan, critiques)
                execution_results = await self._execute_plan(plan)
                critiques = await self._critique_results(request.objective, execution_results)
                iterations += 1
                optimizations_applied.append(f"replan_iteration_{iterations}")
        
        # Determine final status
        if not critiques:
            final_status = TaskStatus.COMPLETED
        elif iterations >= request.max_iterations:
            final_status = TaskStatus.FAILED
        else:
            final_status = TaskStatus.COMPLETED
        
        total_time = (datetime.utcnow() - start_time).total_seconds()
        
        return WorkflowOutput(
            objective=request.objective,
            plan=plan,
            execution_results=execution_results,
            critiques=critiques,
            final_status=final_status,
            iterations=iterations,
            total_time_seconds=total_time,
            optimizations_applied=optimizations_applied
        )
    
    async def _create_plan(self, objective: str, context: dict) -> list[TaskStep]:
        """Create execution plan."""
        # In production, use LLM to generate plan
        return [
            TaskStep(
                step_id="step_1",
                action="gather_information",
                parameters={"sources": ["database", "api"]},
                status=TaskStatus.PENDING
            ),
            TaskStep(
                step_id="step_2",
                action="analyze_data",
                parameters={"method": "statistical"},
                dependencies=["step_1"],
                status=TaskStatus.PENDING
            ),
            TaskStep(
                step_id="step_3",
                action="generate_output",
                parameters={"format": "json"},
                dependencies=["step_2"],
                status=TaskStatus.PENDING
            )
        ]
    
    async def _execute_plan(self, plan: list[TaskStep]) -> dict:
        """Execute the plan."""
        results = {}
        for step in plan:
            step.status = TaskStatus.EXECUTING
            # Simulate execution
            step.result = {"status": "completed", "data": f"{step.action}_result"}
            step.status = TaskStatus.COMPLETED
            results[step.step_id] = step.result
        return results
    
    async def _critique_results(self, objective: str, results: dict) -> list[str]:
        """Critique execution results."""
        # In production, use LLM to critique
        # Return empty list if no issues found
        return []
    
    async def _replan(self, plan: list[TaskStep], critiques: list[str]) -> list[TaskStep]:
        """Re-plan based on critiques."""
        # In production, use LLM to adjust plan
        return plan


# ============================================================================
# Level 5: Multi-Agent Collaboration
# ============================================================================

class CollaborativeAgent(Agent):
    """
    Level 5: Multi-agent collaborative system.
    
    Features:
    - Agent discovery
    - Task delegation
    - Result aggregation
    - A2A protocol support
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_agents = {
            "analyzer": {"capabilities": ["data_analysis", "statistics"]},
            "predictor": {"capabilities": ["prediction", "forecasting"]},
            "validator": {"capabilities": ["validation", "quality_check"]}
        }
    
    async def process(self, request: CollaborationRequest) -> CollaborationResponse:
        """Coordinate multi-agent collaboration."""
        
        start_time = datetime.utcnow()
        
        # Step 1: Find agents with required capabilities
        participating_agents = self._find_agents(request.required_capabilities)
        
        # Step 2: Delegate tasks based on collaboration mode
        if request.collaboration_mode == "sequential":
            individual_results = await self._sequential_execution(
                participating_agents,
                request.task_data
            )
        elif request.collaboration_mode == "parallel":
            individual_results = await self._parallel_execution(
                participating_agents,
                request.task_data
            )
        else:  # consensus
            individual_results = await self._consensus_execution(
                participating_agents,
                request.task_data
            )
        
        # Step 3: Aggregate results
        aggregated_result = self._aggregate_results(individual_results)
        consensus_reached = self._check_consensus(individual_results)
        
        collaboration_time = (datetime.utcnow() - start_time).total_seconds()
        
        return CollaborationResponse(
            task_id=request.task_id,
            participating_agents=participating_agents,
            individual_results=individual_results,
            aggregated_result=aggregated_result,
            consensus_reached=consensus_reached,
            collaboration_time_seconds=collaboration_time,
            a2a_agents_used=[] if not request.use_a2a else ["external_agent_1"]
        )
    
    def _find_agents(self, required_capabilities: list[str]) -> list[str]:
        """Find agents with required capabilities."""
        matching_agents = []
        for agent_id, info in self.available_agents.items():
            if any(cap in info["capabilities"] for cap in required_capabilities):
                matching_agents.append(agent_id)
        return matching_agents
    
    async def _sequential_execution(self, agents: list[str], data: dict) -> dict:
        """Execute agents sequentially."""
        results = {}
        current_data = data
        for agent_id in agents:
            result = await self._call_agent(agent_id, current_data)
            results[agent_id] = result
            current_data = result  # Pass output to next agent
        return results
    
    async def _parallel_execution(self, agents: list[str], data: dict) -> dict:
        """Execute agents in parallel."""
        tasks = [self._call_agent(agent_id, data) for agent_id in agents]
        results_list = await asyncio.gather(*tasks)
        return dict(zip(agents, results_list))
    
    async def _consensus_execution(self, agents: list[str], data: dict) -> dict:
        """Execute agents and seek consensus."""
        # Similar to parallel, but with consensus checking
        results = await self._parallel_execution(agents, data)
        # In production, iterate until consensus
        return results
    
    async def _call_agent(self, agent_id: str, data: dict) -> dict:
        """Call individual agent."""
        # In production, use AgentRouter or A2A client
        return {"agent": agent_id, "result": "processed", "data": data}
    
    def _aggregate_results(self, results: dict) -> dict:
        """Aggregate results from multiple agents."""
        # In production, use sophisticated aggregation logic
        return {
            "summary": "aggregated_results",
            "agent_count": len(results),
            "combined_output": "final_result"
        }
    
    def _check_consensus(self, results: dict) -> bool:
        """Check if agents reached consensus."""
        # In production, implement actual consensus checking
        return True


# ============================================================================
# Demo: Run All Levels
# ============================================================================

async def demo_all_levels():
    """Demonstrate all learning levels with generic schemas."""
    
    print("\n" + "="*70)
    print("Generic Learning Agents (Levels 1-5)")
    print("="*70)
    print("Domain-agnostic schemas that work for any use case!")
    
    # Level 1: Simple Chatbot
    print("\n" + "="*70)
    print("Level 1: Simple Chatbot Agent")
    print("="*70)
    
    chatbot = SimpleChatbotAgent()
    chat_result = await chatbot.process(ChatInput(
        question="Hello, can you help me?",
        user_id="user_123",
        session_id="session_456"
    ))
    print(f"✅ Question: Hello, can you help me?")
    print(f"✅ Answer: {chat_result.answer}")
    print(f"   Confidence: {chat_result.confidence:.2f}")
    
    # Level 2: Context-Aware Agent
    print("\n" + "="*70)
    print("Level 2: Context-Aware Agent")
    print("="*70)
    
    context_agent = ContextAwareAgent()
    context_result = await context_agent.process(ContextAwareInput(
        message="What did we discuss earlier?",
        user_id="user_123",
        session_id="session_789"
    ))
    print(f"✅ Message: What did we discuss earlier?")
    print(f"✅ Response: {context_result.response[:100]}...")
    print(f"   Stored to memory: {context_result.stored_to_memory}")
    
    # Level 3: Production API
    print("\n" + "="*70)
    print("Level 3: Production API Agent")
    print("="*70)
    
    api_agent = ProductionAPIAgent()
    api_result = await api_agent.process(APIRequest(
        endpoint="analyze",
        data={"input": "sample_data"},
        request_id="req_123"
    ))
    print(f"✅ Endpoint: analyze")
    print(f"✅ Success: {api_result.success}")
    print(f"   Processing time: {api_result.processing_time_ms:.2f}ms")
    print(f"   Result: {api_result.data}")
    
    # Level 4: Complex Workflow
    print("\n" + "="*70)
    print("Level 4: Complex Workflow Agent (Plan-Act-Critique)")
    print("="*70)
    
    workflow_agent = WorkflowAgent()
    workflow_result = await workflow_agent.process(WorkflowInput(
        objective="Analyze and generate report",
        context={"data_source": "database"},
        max_iterations=3
    ))
    print(f"✅ Objective: Analyze and generate report")
    print(f"✅ Status: {workflow_result.final_status}")
    print(f"   Plan steps: {len(workflow_result.plan)}")
    print(f"   Iterations: {workflow_result.iterations}")
    print(f"   Total time: {workflow_result.total_time_seconds:.2f}s")
    
    # Level 5: Multi-Agent Collaboration
    print("\n" + "="*70)
    print("Level 5: Multi-Agent Collaboration")
    print("="*70)
    
    collab_agent = CollaborativeAgent()
    collab_result = await collab_agent.process(CollaborationRequest(
        task_id="task_456",
        initiating_agent="coordinator",
        required_capabilities=["data_analysis", "prediction"],
        task_data={"input": "collaborative_task"},
        collaboration_mode="parallel"
    ))
    print(f"✅ Task: Collaborative analysis")
    print(f"✅ Participating agents: {', '.join(collab_result.participating_agents)}")
    print(f"   Consensus reached: {collab_result.consensus_reached}")
    print(f"   Collaboration time: {collab_result.collaboration_time_seconds:.2f}s")
    
    # Summary
    print("\n" + "="*70)
    print("Summary: Generic Schemas for Any Domain")
    print("="*70)
    print("""
These schemas work for ANY use case:
  ✅ Customer support chatbots
  ✅ Data analysis systems
  ✅ Process automation
  ✅ Multi-agent orchestration
  ✅ Any domain you can imagine!

No more fraud-specific schemas!
Build your learning projects with these generic, reusable schemas.

See: shared/schemas/learning.py for all schemas
Use: get_input_schema_for_level(n) to get schema for level n
""")


if __name__ == "__main__":
    asyncio.run(demo_all_levels())

