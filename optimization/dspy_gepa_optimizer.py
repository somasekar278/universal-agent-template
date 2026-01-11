"""
DSPy GEPA Optimizer

Integrates DSPy's GEPA (Generative Edit-based Prompt Adaptation) optimizer
with the SOTA Agent Framework.

DSPy GEPA is specifically designed for optimizing DSPy programs (ChainOfThought,
ReAct, etc.) using LLM-driven reflection and iterative prompt refinement.

Based on: https://dspy.ai/tutorials/gepa_aime/#optimize-the-program-with-dspygepa
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import dspy
from dspy.teleprompt import GEPA


@dataclass
class DSPyGepaResult:
    """Result from DSPy GEPA optimization."""
    original_program: dspy.Module
    optimized_program: dspy.Module
    original_score: Optional[float] = None
    optimized_score: Optional[float] = None
    improvement: Optional[float] = None
    optimizer_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class DSPyGepaOptimizer:
    """
    DSPy GEPA optimizer for DSPy programs.

    GEPA (Generative Edit-based Prompt Adaptation) uses LLM-driven reflection
    to iteratively refine prompts in DSPy programs.

    Best for:
    - DSPy programs (ChainOfThought, ReAct, etc.)
    - Math/reasoning tasks
    - Multi-step workflows
    - When you want programmatic control with DSPy

    Usage:
        import dspy

        # Define DSPy program
        class QA(dspy.Module):
            def __init__(self):
                self.answer = dspy.ChainOfThought("question -> answer")

            def forward(self, question):
                return self.answer(question=question)

        # Optimize with GEPA
        optimizer = DSPyGepaOptimizer(auto="light")

        result = optimizer.optimize(
            program=QA(),
            trainset=trainset,
            valset=valset,
            metric=accuracy_metric
        )

        # Use optimized program
        optimized_qa = result.optimized_program
    """

    def __init__(
        self,
        auto: str = "medium",
        max_bootstrapped_demos: int = 4,
        max_labeled_demos: int = 8,
        max_rounds: int = 3,
        max_errors: int = 5,
        **kwargs
    ):
        """
        Initialize DSPy GEPA optimizer.

        Args:
            auto: Optimization budget:
                - "light": Fast, ~50 metric calls
                - "medium": Balanced, ~200 calls (default)
                - "heavy": Thorough, ~1000 calls
            max_bootstrapped_demos: Max few-shot examples to bootstrap
            max_labeled_demos: Max labeled examples to include
            max_rounds: Max optimization rounds
            max_errors: Max errors before stopping
            **kwargs: Additional GEPA arguments
        """
        self.auto = auto
        self.max_bootstrapped_demos = max_bootstrapped_demos
        self.max_labeled_demos = max_labeled_demos
        self.max_rounds = max_rounds
        self.max_errors = max_errors
        self.kwargs = kwargs

    def optimize(
        self,
        program: dspy.Module,
        trainset: List,
        valset: Optional[List] = None,
        metric: Optional[Callable] = None,
        **kwargs
    ) -> DSPyGepaResult:
        """
        Optimize a DSPy program using GEPA.

        Args:
            program: DSPy Module to optimize
            trainset: Training examples (list of dspy.Example)
            valset: Validation examples (optional)
            metric: Evaluation metric function
            **kwargs: Additional arguments

        Returns:
            DSPyGepaResult with optimized program

        Example:
            # Create program
            qa = dspy.ChainOfThought("question -> answer")

            # Prepare data
            trainset = [
                dspy.Example(question="2+2?", answer="4").with_inputs("question"),
                dspy.Example(question="3+3?", answer="6").with_inputs("question"),
            ]

            # Metric
            def accuracy(example, prediction, trace=None):
                return example.answer == prediction.answer

            # Optimize
            result = optimizer.optimize(
                program=qa,
                trainset=trainset,
                metric=accuracy
            )
        """
        print(f"🔧 Optimizing DSPy program with GEPA...")
        print(f"   Budget: {self.auto}")
        print(f"   Training examples: {len(trainset)}")
        if valset:
            print(f"   Validation examples: {len(valset)}")
        print()

        # Create GEPA teleprompter
        teleprompter = GEPA(
            auto=self.auto,
            max_bootstrapped_demos=self.max_bootstrapped_demos,
            max_labeled_demos=self.max_labeled_demos,
            max_rounds=self.max_rounds,
            max_errors=self.max_errors,
            **self.kwargs
        )

        # Evaluate original program
        original_score = None
        if metric and valset:
            print("📊 Evaluating original program...")
            original_score = self._evaluate(program, valset, metric)
            print(f"   Original score: {original_score:.3f}")
            print()

        # Compile (optimize) with GEPA
        print("⚙️ Compiling with GEPA...")
        optimized_program = teleprompter.compile(
            student=program,
            trainset=trainset,
            valset=valset,
            metric=metric,
            **kwargs
        )
        print("✅ Compilation complete!")
        print()

        # Evaluate optimized program
        optimized_score = None
        improvement = None

        if metric and valset:
            print("📊 Evaluating optimized program...")
            optimized_score = self._evaluate(optimized_program, valset, metric)
            print(f"   Optimized score: {optimized_score:.3f}")

            if original_score is not None:
                improvement = (optimized_score - original_score) / original_score
                print(f"   Improvement: {improvement:.2%}")
            print()

        # Create result
        result = DSPyGepaResult(
            original_program=program,
            optimized_program=optimized_program,
            original_score=original_score,
            optimized_score=optimized_score,
            improvement=improvement,
            optimizer_config={
                "auto": self.auto,
                "max_bootstrapped_demos": self.max_bootstrapped_demos,
                "max_labeled_demos": self.max_labeled_demos,
                "max_rounds": self.max_rounds
            },
            metadata={
                "trainset_size": len(trainset),
                "valset_size": len(valset) if valset else 0,
                "has_metric": metric is not None
            }
        )

        print("=" * 60)
        print("✅ DSPy GEPA Optimization Complete!")
        print("=" * 60)
        print()

        return result

    def _evaluate(
        self,
        program: dspy.Module,
        dataset: List,
        metric: Callable
    ) -> float:
        """Evaluate a program on a dataset."""
        from dspy.evaluate import Evaluate

        evaluator = Evaluate(
            devset=dataset,
            metric=metric,
            num_threads=1,
            display_progress=False
        )

        score = evaluator(program)
        return score

    def extract_prompts(
        self,
        optimized_program: dspy.Module
    ) -> Dict[str, str]:
        """
        Extract optimized prompts from a DSPy program.

        Useful for registering in MLflow Prompt Registry.

        Args:
            optimized_program: Optimized DSPy Module

        Returns:
            Dict mapping module names to prompt templates

        Example:
            prompts = optimizer.extract_prompts(optimized_program)

            # Register in MLflow
            for name, template in prompts.items():
                mlflow.genai.register_prompt(
                    name=f"dspy_{name}",
                    template=template
                )
        """
        prompts = {}

        # Iterate through program's modules
        for name, module in optimized_program.named_predictors():
            if hasattr(module, 'signature'):
                # Extract signature instructions
                if hasattr(module.signature, 'instructions'):
                    prompts[name] = module.signature.instructions
                # Or full signature
                elif hasattr(module.signature, '__doc__'):
                    prompts[name] = module.signature.__doc__

        return prompts


def create_dspy_metric(scorer_fn: Callable, name: str = "custom_metric"):
    """
    Convert a simple scoring function to DSPy metric format.

    Args:
        scorer_fn: Function(expected, predicted) -> float
        name: Metric name

    Returns:
        DSPy-compatible metric function

    Example:
        def accuracy(expected, predicted):
            return 1.0 if expected == predicted else 0.0

        metric = create_dspy_metric(accuracy, "accuracy")

        result = optimizer.optimize(
            program=program,
            trainset=trainset,
            metric=metric
        )
    """
    def dspy_metric(example, pred, trace=None):
        """DSPy metric wrapper."""
        expected = example.answer if hasattr(example, 'answer') else example.output
        predicted = pred.answer if hasattr(pred, 'answer') else pred.output
        return scorer_fn(expected, predicted)

    dspy_metric.__name__ = name
    return dspy_metric


def convert_to_dspy_examples(
    data: List[Dict[str, Any]],
    input_keys: List[str],
    output_key: str = "answer"
) -> List[dspy.Example]:
    """
    Convert standard format to DSPy examples.

    Args:
        data: List of dicts with inputs and outputs
        input_keys: Keys to use as inputs
        output_key: Key to use as output

    Returns:
        List of dspy.Example objects

    Example:
        data = [
            {"question": "2+2?", "answer": "4"},
            {"question": "3+3?", "answer": "6"}
        ]

        examples = convert_to_dspy_examples(
            data=data,
            input_keys=["question"],
            output_key="answer"
        )
    """
    examples = []

    for item in data:
        # Extract inputs
        example_dict = {key: item[key] for key in input_keys if key in item}

        # Add output
        if output_key in item:
            example_dict[output_key] = item[output_key]

        # Create example
        example = dspy.Example(**example_dict).with_inputs(*input_keys)
        examples.append(example)

    return examples
