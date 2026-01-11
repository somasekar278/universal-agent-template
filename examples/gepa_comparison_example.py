"""
GEPA Comparison Example

Demonstrates both DSPy GEPA and MLflow GEPA side-by-side.
Shows how to use both for different scenarios.
"""

import dspy
import mlflow
from optimization import DSPyGepaOptimizer, GepaOptimizer


def example_1_dspy_gepa():
    """Example 1: Using DSPy GEPA for a DSPy program."""

    print("=" * 60)
    print("Example 1: DSPy GEPA")
    print("=" * 60)
    print()

    # Configure DSPy
    api_key = input("Enter your OpenAI API key: ")
    lm = dspy.LM("openai/gpt-4.1-mini", api_key=api_key)
    dspy.configure(lm=lm)

    # Define a simple DSPy program
    class SimpleQA(dspy.Module):
        def __init__(self):
            self.answer = dspy.ChainOfThought("question -> answer")

        def forward(self, question):
            return self.answer(question=question)

    # Prepare training data
    trainset = [
        dspy.Example(question="What is 2+2?", answer="4").with_inputs("question"),
        dspy.Example(question="What is 3+3?", answer="6").with_inputs("question"),
        dspy.Example(question="What is 5*5?", answer="25").with_inputs("question"),
        dspy.Example(question="What is 10-3?", answer="7").with_inputs("question"),
    ]

    valset = [
        dspy.Example(question="What is 7+8?", answer="15").with_inputs("question"),
        dspy.Example(question="What is 4*6?", answer="24").with_inputs("question"),
    ]

    # Define accuracy metric
    def accuracy(example, pred, trace=None):
        return 1.0 if example.answer.strip() == pred.answer.strip() else 0.0

    # Optimize with DSPy GEPA
    print("🔧 Optimizing with DSPy GEPA...")
    optimizer = DSPyGepaOptimizer(auto="light")

    result = optimizer.optimize(
        program=SimpleQA(),
        trainset=trainset,
        valset=valset,
        metric=accuracy
    )

    print()
    print("✅ Results:")
    print(f"   Original score: {result.original_score:.2%}")
    print(f"   Optimized score: {result.optimized_score:.2%}")
    print(f"   Improvement: {result.improvement:.2%}")
    print()

    # Test optimized program
    test_question = "What is 9+6?"
    answer = result.optimized_program(question=test_question)
    print(f"📝 Test: {test_question}")
    print(f"   Answer: {answer.answer}")
    print()

    return result


def example_2_mlflow_gepa():
    """Example 2: Using MLflow GEPA for any function."""

    print("=" * 60)
    print("Example 2: MLflow GEPA")
    print("=" * 60)
    print()

    # Set up MLflow
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment("/Shared/gepa_comparison")

    # Define a simple agent (non-DSPy)
    def simple_qa_agent(question: str) -> str:
        """Simple QA agent using MLflow prompt."""
        prompt = mlflow.genai.load_prompt("prompts:/simple_qa@latest")

        # For demo, just format the prompt
        # In production, you'd call an LLM here
        return f"Based on '{prompt.template}': Calculating {question}..."

    # Register initial prompt
    prompt = mlflow.genai.register_prompt(
        name="simple_qa",
        template="You are a math tutor. Answer: {{question}}"
    )

    print(f"📝 Registered prompt: {prompt.uri}")
    print()

    # Training data
    train_data = [
        {
            "inputs": {"question": "What is 2+2?"},
            "expectations": {"expected_response": "4"}
        },
        {
            "inputs": {"question": "What is 3+3?"},
            "expectations": {"expected_response": "6"}
        },
        {
            "inputs": {"question": "What is 5*5?"},
            "expectations": {"expected_response": "25"}
        },
    ]

    # Optimize with MLflow GEPA
    print("🔧 Optimizing with MLflow GEPA...")
    optimizer = GepaOptimizer(
        reflection_model="databricks-claude-sonnet-4",
        max_metric_calls=50
    )

    result = optimizer.optimize(
        predict_fn=lambda inputs: simple_qa_agent(inputs["question"]),
        train_data=train_data,
        prompt_uris=[prompt.uri],
        scorers=["correctness"]
    )

    print()
    print("✅ Results:")
    print(f"   Optimized prompt: {result.optimized_prompts[0].uri}")
    if result.improvement:
        print(f"   Improvement: {result.improvement:.2%}")
    print()

    return result


def example_3_comparison():
    """Example 3: Side-by-side comparison."""

    print("=" * 60)
    print("Example 3: Which GEPA Should You Use?")
    print("=" * 60)
    print()

    comparison = """
    ┌─────────────────────┬──────────────┬────────────────┐
    │ Scenario            │ DSPy GEPA    │ MLflow GEPA    │
    ├─────────────────────┼──────────────┼────────────────┤
    │ Using DSPy modules  │ ✅ Best      │ ❌ Not needed  │
    │ Any Python function │ ❌ Can't use │ ✅ Best        │
    │ Programmatic control│ ✅ Yes       │ ❌ Limited     │
    │ Framework-agnostic  │ ❌ No        │ ✅ Yes         │
    │ MLflow integration  │ ⚠️  Manual   │ ✅ Native      │
    │ Production ready    │ ⚠️  Extract  │ ✅ Direct      │
    └─────────────────────┴──────────────┴────────────────┘

    Recommendation:
    - New DSPy project → Use DSPy GEPA
    - Existing agent → Use MLflow GEPA
    - Want both → DSPy GEPA → Extract → MLflow Registry
    """

    print(comparison)
    print()


def example_4_dspy_production_optimization():
    """Example 4: DSPy GEPA for production optimization with MLflow integration."""

    print("=" * 60)
    print("Example 4: DSPy GEPA for Production Optimization")
    print("=" * 60)
    print()

    print("This example demonstrates:")
    print("  - Reading production data from MLflow")
    print("  - Using MLflow scorers as DSPy metrics")
    print("  - Optimizing DSPy programs with production feedback")
    print("  - Pushing optimized prompts to UC Prompt Registry")
    print()

    # Configure DSPy
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ")
    if not api_key:
        print("⏭️  Skipping (no API key provided)")
        return

    lm = dspy.LM("openai/gpt-4.1-mini", api_key=api_key)
    dspy.configure(lm=lm)

    # Production agent
    class ProductionAgent(dspy.Module):
        def __init__(self):
            self.answer = dspy.ChainOfThought("query -> response")

        def forward(self, query):
            return self.answer(query=query)

    # Simulate production data (normally loaded from MLflow)
    print("📊 Loading production data...")
    trainset = [
        dspy.Example(
            query="How do I reset my password?",
            response="Click 'Forgot Password' and follow the email link."
        ).with_inputs("query"),
        dspy.Example(
            query="What's your refund policy?",
            response="We offer 30-day refunds for unopened items."
        ).with_inputs("query"),
        dspy.Example(
            query="How long does shipping take?",
            response="Standard shipping takes 3-5 business days."
        ).with_inputs("query"),
        dspy.Example(
            query="Do you ship internationally?",
            response="Yes, we ship to over 100 countries worldwide."
        ).with_inputs("query"),
    ]

    valset = [
        dspy.Example(
            query="Can I track my order?",
            response="Yes, check your email for a tracking link."
        ).with_inputs("query"),
    ]

    print(f"   Loaded {len(trainset)} training examples from production")
    print(f"   Loaded {len(valset)} validation examples")
    print()

    # Define metric using MLflow-style scoring
    def mlflow_based_metric(example, pred, trace=None):
        """Simulates MLflow scorer (e.g., Correctness, Relevance)"""
        # In production, you would use:
        # from mlflow.genai.scorers import Correctness
        # scorer = Correctness(model="databricks-claude-sonnet-4")
        # return scorer(outputs=pred.response, expectations={"expected_response": example.response})

        # Simplified correctness check
        pred_lower = pred.response.lower()
        expected_lower = example.response.lower()

        # Check if key terms are present
        expected_terms = set(expected_lower.split())
        pred_terms = set(pred_lower.split())
        overlap = len(expected_terms & pred_terms) / len(expected_terms) if expected_terms else 0

        return overlap

    print("🔧 Starting DSPy GEPA optimization...")
    optimizer = DSPyGepaOptimizer(auto="light")

    result = optimizer.optimize(
        program=ProductionAgent(),
        trainset=trainset,
        valset=valset,
        metric=mlflow_based_metric
    )

    print()
    print(f"✅ Optimization complete!")
    print(f"   Initial Score: {result.initial_score:.2f}")
    print(f"   Final Score: {result.final_score:.2f}")
    print(f"   Improvement: {result.improvement*100:.1f}%")
    print()

    # Extract optimized prompts
    print("📦 Extracting optimized prompts...")
    prompts = optimizer.extract_prompts(result.optimized_program)

    for module_name, prompt_template in prompts.items():
        print(f"\n   Module: {module_name}")
        print(f"   Prompt: {prompt_template[:100]}...")

    print()
    print("💡 In production, you would now:")
    print("   1. Register prompts to UC Prompt Registry via mlflow.genai.register_prompt()")
    print("   2. Set up automated pipelines to run daily/weekly optimization")
    print("   3. Use A/B testing to validate improvements")
    print("   4. Auto-promote versions with significant gains")
    print()

    # Test the optimized agent
    print("🧪 Testing optimized agent...")
    optimized_agent = result.optimized_program

    test_query = "How do I cancel my order?"
    response = optimized_agent(query=test_query)

    print(f"   Query: {test_query}")
    print(f"   Response: {response.response}")
    print()


def main():
    """Run all examples."""

    print()
    print("=" * 60)
    print("GEPA Comparison Examples")
    print("=" * 60)
    print()

    print("This example demonstrates:")
    print("1. DSPy GEPA - For DSPy programs")
    print("2. MLflow GEPA - For any function")
    print("3. Comparison - Which to use when")
    print("4. DSPy GEPA for Production (with MLflow integration)")
    print()

    choice = input("Run which example? (1/2/3/4/all): ").strip()

    if choice == "1" or choice == "all":
        example_1_dspy_gepa()

    if choice == "2" or choice == "all":
        example_2_mlflow_gepa()

    if choice == "3" or choice == "all":
        example_3_comparison()

    if choice == "4" or choice == "all":
        example_4_dspy_production_optimization()

    print()
    print("=" * 60)
    print("✅ Examples Complete!")
    print("=" * 60)
    print()
    print("See docs/COMPLETE_GEPA_GUIDE.md for full documentation.")
    print()


if __name__ == "__main__":
    main()
