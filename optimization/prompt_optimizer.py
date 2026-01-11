"""
Unified Prompt Optimizer

Combines DSPy, TextGrad, and GEPA for comprehensive prompt optimization:
- Task prompts → DSPy
- System prompts → TextGrad
- Production prompts → GEPA (MLflow)
- Automated pipelines
- Multi-stage optimization
- Unity Catalog integration

Configuration loaded from YAML (optimization.*)
"""

from typing import List, Dict, Any, Optional, Literal, Callable
from dataclasses import dataclass, field
from datetime import datetime

from .dspy_optimizer import DSPyOptimizer, OptimizationResult
from .textgrad_optimizer import TextGradOptimizer, SystemPromptResult
from .gepa_optimizer import GepaOptimizer, GepaResult
from .dspy_gepa_optimizer import DSPyGepaOptimizer, DSPyGepaResult


@dataclass
class PromptCandidate:
    """A candidate prompt with metadata."""
    prompt: str
    prompt_type: Literal["system", "task"]
    score: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class PromptOptimizer:
    """
    Unified prompt optimizer using DSPy and TextGrad.

    Automatically selects the right optimizer based on prompt type.

    Usage:
        optimizer = PromptOptimizer()

        # Optimize system prompt
        result = await optimizer.optimize(
            prompt="You are an expert.",
            prompt_type="system",
            evaluation_data=eval_data
        )

        # Optimize task prompt
        result = await optimizer.optimize(
            prompt="Classify fraud",
            prompt_type="task",
            training_data=train_data
        )
    """

    def __init__(
        self,
        gepa_reflection_model: str = "databricks-claude-sonnet-4",
        gepa_max_calls: int = 100,
        dspy_gepa_auto: str = "medium"
    ):
        """
        Initialize prompt optimizer.

        Args:
            gepa_reflection_model: Model for MLflow GEPA reflection
            gepa_max_calls: Max optimization iterations for MLflow GEPA
            dspy_gepa_auto: Budget for DSPy GEPA (light/medium/heavy)
        """
        self.dspy_optimizer = DSPyOptimizer()
        self.textgrad_optimizer = TextGradOptimizer()
        self.gepa_optimizer = GepaOptimizer(
            reflection_model=gepa_reflection_model,
            max_metric_calls=gepa_max_calls
        )
        self.dspy_gepa_optimizer = DSPyGepaOptimizer(auto=dspy_gepa_auto)
        self.optimization_history = []

    async def optimize(
        self,
        prompt: str,
        prompt_type: Literal["system", "task"],
        training_data: Optional[List[Dict[str, Any]]] = None,
        evaluation_data: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """
        Optimize prompt using appropriate method.

        Args:
            prompt: Initial prompt
            prompt_type: "system" or "task"
            training_data: Training data (for DSPy)
            evaluation_data: Evaluation data (for TextGrad)
            **kwargs: Additional arguments

        Returns:
            OptimizationResult or SystemPromptResult
        """
        if prompt_type == "task":
            if training_data is None:
                raise ValueError("training_data required for task prompt optimization")

            result = await self.dspy_optimizer.optimize(
                task=kwargs.get("task", "general"),
                training_data=training_data,
                metric=kwargs.get("metric"),
                dev_data=evaluation_data
            )

            # Store in history
            self.optimization_history.append({
                "type": "task",
                "result": result,
                "timestamp": datetime.now()
            })

            # Save to Unity Catalog if available
            await self._save_to_uc(result, "task")

            return result

        elif prompt_type == "system":
            if evaluation_data is None:
                raise ValueError("evaluation_data required for system prompt optimization")

            result = await self.textgrad_optimizer.optimize(
                system_prompt=prompt,
                evaluation_data=evaluation_data,
                objective=kwargs.get("objective"),
                constraints=kwargs.get("constraints")
            )

            # Store in history
            self.optimization_history.append({
                "type": "system",
                "result": result,
                "timestamp": datetime.now()
            })

            # Save to Unity Catalog if available
            await self._save_to_uc(result, "system")

            return result

        else:
            raise ValueError(f"Unknown prompt_type: {prompt_type}")

    def optimize_with_gepa(
        self,
        predict_fn: Callable,
        train_data: List[Dict[str, Any]],
        prompt_uris: List[str],
        scorers: Optional[List[Any]] = None,
        **kwargs
    ) -> GepaResult:
        """
        Optimize prompts using GEPA (MLflow).

        Best for:
        - Production prompt optimization
        - Multi-prompt agent workflows
        - When you have real usage data
        - Model migration scenarios

        Args:
            predict_fn: Agent function that uses the prompts
            train_data: Training examples in MLflow format
            prompt_uris: List of prompt URIs (e.g., ["prompts:/qa/1"])
            scorers: Evaluation metrics (default: ["correctness"])
            **kwargs: Additional GEPA arguments

        Returns:
            GepaResult with optimized prompts

        Example:
            # Define agent function
            def my_agent(question: str) -> str:
                prompt = mlflow.genai.load_prompt("prompts:/qa/1")
                return llm.call(prompt.format(question=question))

            # Prepare training data
            train_data = [
                {
                    "inputs": {"question": "What is 2+2?"},
                    "expectations": {"expected_response": "4"}
                }
            ]

            # Optimize
            optimizer = PromptOptimizer()
            result = optimizer.optimize_with_gepa(
                predict_fn=my_agent,
                train_data=train_data,
                prompt_uris=["prompts:/qa/1"],
                scorers=["correctness", "safety"]
            )
        """
        result = self.gepa_optimizer.optimize(
            predict_fn=predict_fn,
            train_data=train_data,
            prompt_uris=prompt_uris,
            scorers=scorers,
            **kwargs
        )

        # Store in history
        self.optimization_history.append({
            "type": "gepa",
            "result": result,
            "timestamp": datetime.now()
        })

        return result

    def optimize_with_dspy_gepa(
        self,
        program: Any,  # dspy.Module
        trainset: List,
        valset: Optional[List] = None,
        metric: Optional[Callable] = None,
        **kwargs
    ) -> DSPyGepaResult:
        """
        Optimize DSPy programs using DSPy's GEPA optimizer.

        Best for:
        - DSPy programs (ChainOfThought, ReAct, etc.)
        - Math/reasoning tasks
        - Multi-step workflows
        - When you want DSPy's programmatic control

        Args:
            program: DSPy Module to optimize
            trainset: Training examples (list of dspy.Example)
            valset: Validation examples (optional)
            metric: Evaluation metric function
            **kwargs: Additional DSPy GEPA arguments

        Returns:
            DSPyGepaResult with optimized program

        Example:
            import dspy

            # Define DSPy program
            class QA(dspy.Module):
                def __init__(self):
                    self.answer = dspy.ChainOfThought("question -> answer")

                def forward(self, question):
                    return self.answer(question=question)

            # Prepare data
            trainset = [
                dspy.Example(question="2+2?", answer="4").with_inputs("question")
            ]

            # Optimize
            optimizer = PromptOptimizer()
            result = optimizer.optimize_with_dspy_gepa(
                program=QA(),
                trainset=trainset,
                metric=lambda ex, pred, _: ex.answer == pred.answer
            )

            # Use optimized
            optimized_qa = result.optimized_program
        """
        result = self.dspy_gepa_optimizer.optimize(
            program=program,
            trainset=trainset,
            valset=valset,
            metric=metric,
            **kwargs
        )

        # Store in history
        self.optimization_history.append({
            "type": "dspy_gepa",
            "result": result,
            "timestamp": datetime.now()
        })

        return result

    async def _save_to_uc(self, result, prompt_type: str):
        """Save optimization result to Unity Catalog."""
        try:
            from uc_registry.prompt_registry import PromptRegistry

            registry = PromptRegistry()

            # Register optimized prompt
            if prompt_type == "task":
                registry.register_prompt(
                    name=f"optimized_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    content=result.optimized_prompt,
                    metadata={
                        "type": "task",
                        "original_score": result.original_score,
                        "optimized_score": result.optimized_score,
                        "improvement": result.improvement,
                        "method": "dspy"
                    }
                )
            else:
                registry.register_prompt(
                    name=f"optimized_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    content=result.optimized_prompt,
                    metadata={
                        "type": "system",
                        "original_score": result.original_score,
                        "optimized_score": result.optimized_score,
                        "improvement": result.improvement,
                        "method": "textgrad"
                    }
                )

            print(f"✅ Saved optimized prompt to Unity Catalog")

        except Exception as e:
            print(f"⚠️  Could not save to UC: {e}")

    def get_history(self) -> List[Dict[str, Any]]:
        """Get optimization history."""
        return self.optimization_history

    def get_best_candidate(self, prompt_type: str) -> Optional[PromptCandidate]:
        """Get best candidate for a prompt type."""
        candidates = [
            h for h in self.optimization_history
            if h["type"] == prompt_type
        ]

        if not candidates:
            return None

        best = max(candidates, key=lambda x: x["result"].optimized_score)

        return PromptCandidate(
            prompt=best["result"].optimized_prompt,
            prompt_type=prompt_type,
            score=best["result"].optimized_score,
            metadata=best["result"].metadata,
            timestamp=best["timestamp"]
        )


class OptimizationPipeline:
    """
    Multi-stage optimization pipeline.

    Orchestrates multiple optimization steps:
    1. System prompt optimization
    2. Task prompt optimization
    3. A/B testing
    4. Deployment

    Usage:
        pipeline = OptimizationPipeline()

        result = await pipeline.run(
            agent_config={
                "system_prompt": "...",
                "task_prompt": "..."
            },
            training_data=train_data,
            evaluation_data=eval_data
        )
    """

    def __init__(self):
        """Initialize optimization pipeline."""
        self.optimizer = PromptOptimizer()
        self.pipeline_runs = []

    async def run(
        self,
        agent_config: Dict[str, Any],
        training_data: List[Dict[str, Any]],
        evaluation_data: List[Dict[str, Any]],
        stages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run optimization pipeline.

        Args:
            agent_config: Agent configuration with prompts
            training_data: Training data
            evaluation_data: Evaluation data
            stages: Optional stages to run (default: all)

        Returns:
            Optimized configuration
        """
        if stages is None:
            stages = ["system", "task", "test"]

        results = {
            "original_config": agent_config.copy(),
            "optimized_config": agent_config.copy(),
            "stages": {}
        }

        # Stage 1: System prompt optimization
        if "system" in stages and "system_prompt" in agent_config:
            print("🔧 Stage 1: Optimizing system prompt...")

            system_result = await self.optimizer.optimize(
                prompt=agent_config["system_prompt"],
                prompt_type="system",
                evaluation_data=evaluation_data
            )

            results["optimized_config"]["system_prompt"] = system_result.optimized_prompt
            results["stages"]["system"] = {
                "improvement": system_result.improvement,
                "score": system_result.optimized_score
            }

            print(f"✅ System prompt improved by {system_result.improvement:.2%}")

        # Stage 2: Task prompt optimization
        if "task" in stages and "task_prompt" in agent_config:
            print("🔧 Stage 2: Optimizing task prompt...")

            task_result = await self.optimizer.optimize(
                prompt=agent_config.get("task_prompt", ""),
                prompt_type="task",
                training_data=training_data,
                evaluation_data=evaluation_data,
                task=agent_config.get("name", "agent")
            )

            results["optimized_config"]["task_prompt"] = task_result.optimized_prompt
            results["stages"]["task"] = {
                "improvement": task_result.improvement,
                "score": task_result.optimized_score
            }

            print(f"✅ Task prompt improved by {task_result.improvement:.2%}")

        # Stage 3: A/B testing (if requested)
        if "test" in stages:
            print("🔧 Stage 3: A/B testing...")
            from .ab_testing import ABTestFramework

            ab_framework = ABTestFramework()

            # Test original vs optimized
            test_result = await ab_framework.run_test(
                variants=[
                    {"name": "original", "config": results["original_config"]},
                    {"name": "optimized", "config": results["optimized_config"]}
                ],
                test_data=evaluation_data
            )

            results["stages"]["ab_test"] = test_result

            print(f"✅ A/B test complete. Winner: {test_result['winner']}")

        # Store pipeline run
        self.pipeline_runs.append({
            "timestamp": datetime.now(),
            "results": results
        })

        return results
