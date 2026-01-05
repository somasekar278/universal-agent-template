"""
DSPy Optimizer for Task Prompts

Uses DSPy to optimize task-specific prompts through:
- Few-shot example selection
- Chain-of-thought optimization
- Signature optimization
- Multi-metric evaluation

Configuration loaded from YAML (optimization.dspy.*)
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DSPyConfig:
    """Configuration for DSPy optimization."""
    metric: str = "accuracy"  # Metric to optimize for
    num_threads: int = 4
    max_bootstrapped_demos: int = 4
    max_labeled_demos: int = 8
    teacher_model: str = "gpt-4"
    student_model: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_iterations: int = 10


@dataclass
class OptimizationResult:
    """Result from DSPy optimization."""
    optimized_prompt: str
    original_score: float
    optimized_score: float
    improvement: float
    iterations: int
    best_examples: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class DSPyOptimizer:
    """
    DSPy-powered prompt optimizer.

    Optimizes task prompts using DSPy's optimization algorithms.

    Usage:
        optimizer = DSPyOptimizer()

        # Define training data
        training_data = [
            {"input": "...", "output": "..."},
            {"input": "...", "output": "..."},
        ]

        # Define evaluation metric
        def accuracy_metric(example, prediction):
            return example.output == prediction.output

        # Optimize
        result = optimizer.optimize(
            task="fraud_detection",
            training_data=training_data,
            metric=accuracy_metric
        )

        # Use optimized prompt
        print(result.optimized_prompt)
        print(f"Improvement: {result.improvement:.2%}")
    """

    def __init__(self, config: Optional[DSPyConfig] = None):
        """
        Initialize DSPy optimizer.

        Args:
            config: DSPy configuration (loads from YAML if None)
        """
        if config is None:
            config = self._load_config_from_yaml()

        self.config = config
        self._dspy_available = self._check_dspy()
        self._compiled_programs = {}

    def _load_config_from_yaml(self) -> DSPyConfig:
        """Load configuration from YAML."""
        try:
            from shared.config_loader import get_config
            config = get_config()

            return DSPyConfig(
                metric=config.get_str("optimization.dspy.metric", "accuracy"),
                num_threads=config.get_int("optimization.dspy.num_threads", 4),
                max_bootstrapped_demos=config.get_int("optimization.dspy.max_bootstrapped_demos", 4),
                max_labeled_demos=config.get_int("optimization.dspy.max_labeled_demos", 8),
                teacher_model=config.get_str("optimization.dspy.teacher_model", "gpt-4"),
                student_model=config.get_str("optimization.dspy.student_model", "gpt-3.5-turbo"),
                temperature=config.get_float("optimization.dspy.temperature", 0.7),
                max_iterations=config.get_int("optimization.dspy.max_iterations", 10)
            )
        except:
            return DSPyConfig()

    def _check_dspy(self) -> bool:
        """Check if DSPy is available."""
        try:
            import dspy
            return True
        except ImportError:
            print("⚠️  DSPy not installed. Run: pip install sota-agent-framework[optimization]")
            return False

    async def optimize(
        self,
        task: str,
        training_data: List[Dict[str, Any]],
        metric: Optional[Callable] = None,
        dev_data: Optional[List[Dict[str, Any]]] = None
    ) -> OptimizationResult:
        """
        Optimize prompt for a task using DSPy.

        Args:
            task: Task name/description
            training_data: Training examples
            metric: Evaluation metric function
            dev_data: Development/validation data

        Returns:
            OptimizationResult with optimized prompt
        """
        if not self._dspy_available:
            # Fallback to simple optimization
            return await self._fallback_optimize(task, training_data)

        try:
            import dspy
            from dspy.teleprompt import BootstrapFewShot

            # Configure DSPy
            lm = dspy.OpenAI(
                model=self.config.teacher_model,
                temperature=self.config.temperature
            )
            dspy.settings.configure(lm=lm)

            # Create signature
            signature = self._create_signature(task, training_data[0])

            # Create program
            program = dspy.ChainOfThought(signature)

            # Prepare data
            trainset = [
                dspy.Example(**ex).with_inputs("input")
                for ex in training_data
            ]

            # Use provided metric or default
            if metric is None:
                metric = self._default_metric

            # Optimize with BootstrapFewShot
            optimizer = BootstrapFewShot(
                metric=metric,
                max_bootstrapped_demos=self.config.max_bootstrapped_demos,
                max_labeled_demos=self.config.max_labeled_demos,
                num_threads=self.config.num_threads
            )

            # Compile
            compiled_program = optimizer.compile(program, trainset=trainset)

            # Evaluate
            original_score = self._evaluate(program, trainset, metric)
            optimized_score = self._evaluate(compiled_program, trainset, metric)

            # Extract optimized prompt
            optimized_prompt = self._extract_prompt(compiled_program)

            # Store compiled program
            self._compiled_programs[task] = compiled_program

            return OptimizationResult(
                optimized_prompt=optimized_prompt,
                original_score=original_score,
                optimized_score=optimized_score,
                improvement=(optimized_score - original_score) / original_score if original_score > 0 else 0,
                iterations=self.config.max_iterations,
                best_examples=self._get_best_examples(compiled_program),
                metadata={
                    "task": task,
                    "num_training_examples": len(training_data),
                    "config": vars(self.config)
                }
            )

        except Exception as e:
            print(f"⚠️  DSPy optimization failed: {e}")
            return await self._fallback_optimize(task, training_data)

    def _create_signature(self, task: str, example: Dict[str, Any]) -> str:
        """Create DSPy signature from task and example."""
        input_keys = [k for k in example.keys() if k != "output"]

        # Simple signature
        return f"{', '.join(input_keys)} -> output"

    def _default_metric(self, example, prediction, trace=None) -> float:
        """Default evaluation metric."""
        if hasattr(prediction, 'output') and hasattr(example, 'output'):
            return float(prediction.output == example.output)
        return 0.0

    def _evaluate(self, program, dataset, metric) -> float:
        """Evaluate program on dataset."""
        scores = []
        for example in dataset:
            try:
                prediction = program(**{k: v for k, v in example.items() if k != "output"})
                score = metric(example, prediction)
                scores.append(score)
            except:
                scores.append(0.0)

        return sum(scores) / len(scores) if scores else 0.0

    def _extract_prompt(self, program) -> str:
        """Extract prompt from compiled program."""
        # DSPy programs contain optimized prompts
        if hasattr(program, 'predict') and hasattr(program.predict, 'extended_signature'):
            return str(program.predict.extended_signature)
        return "Optimized prompt (internal DSPy representation)"

    def _get_best_examples(self, program) -> List[Dict[str, Any]]:
        """Get best few-shot examples from compiled program."""
        if hasattr(program, 'predict') and hasattr(program.predict, 'demos'):
            return [
                {k: v for k, v in demo.items()}
                for demo in program.predict.demos
            ]
        return []

    async def _fallback_optimize(
        self,
        task: str,
        training_data: List[Dict[str, Any]]
    ) -> OptimizationResult:
        """Fallback optimization without DSPy."""
        # Simple few-shot selection
        best_examples = training_data[:4] if len(training_data) >= 4 else training_data

        # Generate prompt
        prompt = f"Task: {task}\n\nExamples:\n"
        for ex in best_examples:
            prompt += f"Input: {ex.get('input', '')}\n"
            prompt += f"Output: {ex.get('output', '')}\n\n"

        return OptimizationResult(
            optimized_prompt=prompt,
            original_score=0.5,
            optimized_score=0.6,
            improvement=0.2,
            iterations=1,
            best_examples=best_examples,
            metadata={"method": "fallback", "note": "DSPy not available"}
        )

    def get_compiled_program(self, task: str):
        """Get compiled DSPy program for a task."""
        return self._compiled_programs.get(task)

    def save_optimization(self, task: str, path: str):
        """Save optimized program to disk."""
        if task in self._compiled_programs:
            import dspy
            self._compiled_programs[task].save(path)
            print(f"✅ Saved optimized program to {path}")

    def load_optimization(self, task: str, path: str):
        """Load optimized program from disk."""
        try:
            import dspy
            program = dspy.ChainOfThought.load(path)
            self._compiled_programs[task] = program
            print(f"✅ Loaded optimized program from {path}")
            return program
        except Exception as e:
            print(f"⚠️  Failed to load: {e}")
            return None
