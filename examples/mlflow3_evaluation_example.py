"""
MLflow 3 Evaluation Example

Shows how to use the turnkey evaluation with MLflow 3's default scorers:
- Correctness (compares against ground truth)
- Groundedness (checks if grounded in context)
- Relevance (checks relevance to query)
- Safety (checks for harmful content)
- Custom Guidelines

Based on: https://docs.databricks.com/aws/en/mlflow3/genai/agent-eval-migration
"""

import mlflow
from typing import Dict, Any
from optimization.turnkey_optimizer import TurnkeyOptimizer


# ============================================================================
# Example 1: Simple Evaluation with Correctness & Relevance
# ============================================================================

def example_simple_evaluation():
    """Evaluate an agent with basic scorers."""

    # Define your agent's prediction function
    def my_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Your agent function.

        Takes inputs dict, returns outputs dict.
        """
        query = inputs.get("input", "")

        # Your agent logic here (LLM call, reasoning, etc.)
        response = f"This is my response to: {query}"

        return {"response": response}

    # Prepare evaluation data (MLflow 3 format)
    eval_data = [
        {
            "inputs": {"input": "What is MLflow?"},
            "outputs": {"response": "MLflow is an open-source platform for managing the ML lifecycle."},
            "expectations": {
                "expected_response": "MLflow is an open-source platform for managing the ML lifecycle."
            }
        },
        {
            "inputs": {"input": "What is Databricks?"},
            "outputs": {"response": "Databricks is a unified analytics platform for big data and AI."},
            "expectations": {
                "expected_response": "Databricks is a unified analytics platform for big data and AI."
            }
        },
        {
            "inputs": {"input": "How do I create a cluster?"},
            "outputs": {"response": "Go to Compute > Create Cluster in the Databricks UI."},
            "expectations": {
                "expected_response": "Navigate to the Compute tab and click Create Cluster."
            }
        }
    ]

    # Initialize optimizer
    optimizer = TurnkeyOptimizer(config_path="config/agent_config.yaml")

    # Run evaluation
    results = optimizer.evaluate_agent(
        agent_name="my_agent",
        predict_fn=my_agent,
        eval_data=eval_data,
        use_groundedness=False,  # No context provided, skip groundedness
        custom_guidelines=None
    )

    print(f"\n✅ Evaluation Complete!")
    print(f"Run ID: {results['run_id']}")
    print(f"Metrics: {results['metrics']}")


# ============================================================================
# Example 2: RAG Agent Evaluation with Groundedness
# ============================================================================

def example_rag_evaluation():
    """Evaluate a RAG agent with groundedness checking."""

    # RAG agent that uses retrieved context
    def rag_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """RAG agent that uses context."""
        query = inputs.get("input", "")
        context = inputs.get("context", "")

        # Your RAG logic here
        # (retrieve docs, pass to LLM, etc.)
        response = f"Based on the context: {context[:100]}..., here's my answer to {query}"

        return {"response": response}

    # Evaluation data with context
    eval_data = [
        {
            "inputs": {
                "input": "What are the key features of MLflow?",
                "context": """
                MLflow is an open-source platform for the ML lifecycle.
                Key features include:
                1. Experiment tracking
                2. Model registry
                3. Model deployment
                4. Model monitoring
                """
            },
            "outputs": {
                "response": "MLflow's key features are experiment tracking, model registry, deployment, and monitoring."
            },
            "expectations": {
                "expected_response": "MLflow provides experiment tracking, model registry, deployment capabilities, and monitoring."
            }
        },
        {
            "inputs": {
                "input": "How does Unity Catalog work?",
                "context": """
                Unity Catalog provides centralized governance for data and AI assets.
                It includes fine-grained access control, data lineage tracking,
                and unified metadata management across clouds.
                """
            },
            "outputs": {
                "response": "Unity Catalog offers centralized governance with access control and lineage tracking."
            },
            "expectations": {
                "expected_response": "Unity Catalog provides governance through access control, lineage, and metadata management."
            }
        }
    ]

    optimizer = TurnkeyOptimizer(config_path="config/agent_config.yaml")

    # Run evaluation with groundedness
    results = optimizer.evaluate_agent(
        agent_name="rag_agent",
        predict_fn=rag_agent,
        eval_data=eval_data,
        use_groundedness=True,  # ✅ Enable groundedness checking
        custom_guidelines=None
    )

    print(f"\n✅ RAG Evaluation Complete!")
    print(f"Metrics: {results['metrics']}")

    # Check groundedness specifically
    if 'groundedness_pass_rate' in results['metrics']:
        groundedness = results['metrics']['groundedness_pass_rate']
        print(f"Groundedness Pass Rate: {groundedness:.1%}")


# ============================================================================
# Example 3: Custom Guidelines Evaluation
# ============================================================================

def example_custom_guidelines():
    """Evaluate with custom guidelines."""

    def support_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Customer support agent."""
        query = inputs.get("input", "")
        response = f"Thank you for contacting support. Regarding {query}, I can help you..."
        return {"response": response}

    eval_data = [
        {
            "inputs": {"input": "I need help with my account"},
            "outputs": {"response": "Thank you for contacting us. I'd be happy to help with your account."},
            "expectations": {"expected_response": "I can help you with your account."}
        },
        {
            "inputs": {"input": "My payment failed"},
            "outputs": {"response": "I apologize for the payment issue. Let me investigate that for you."},
            "expectations": {"expected_response": "Let me help you resolve the payment issue."}
        }
    ]

    # Define custom guidelines
    custom_guidelines = {
        "empathy": [
            "Response must show empathy and understanding",
            "Acknowledge the customer's concern",
            "Use polite and professional language"
        ],
        "actionability": [
            "Response must provide clear next steps",
            "Avoid vague statements",
            "Offer specific help or solutions"
        ],
        "brand_voice": [
            "Use friendly, conversational tone",
            "Avoid overly formal language",
            "Maintain professional boundaries"
        ]
    }

    optimizer = TurnkeyOptimizer(config_path="config/agent_config.yaml")

    results = optimizer.evaluate_agent(
        agent_name="support_agent",
        predict_fn=support_agent,
        eval_data=eval_data,
        use_groundedness=False,
        custom_guidelines=custom_guidelines  # ✅ Custom guidelines
    )

    print(f"\n✅ Custom Guidelines Evaluation Complete!")
    print(f"Metrics: {results['metrics']}")

    # Check custom guideline scores
    for guideline_name in custom_guidelines.keys():
        metric_key = f"{guideline_name}_pass_rate"
        if metric_key in results['metrics']:
            print(f"{guideline_name}: {results['metrics'][metric_key]:.1%}")


# ============================================================================
# Example 4: Per-Example Guidelines with ExpectationsGuidelines
# ============================================================================

def example_expectations_guidelines():
    """
    Use ExpectationsGuidelines when each example has its own specific guidelines.

    Difference:
    - Guidelines: Same rules for ALL examples
    - ExpectationsGuidelines: Different rules PER example
    """

    def my_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Your agent logic
        return {"response": "agent response"}

    # Each example has DIFFERENT guidelines in expectations
    eval_data = [
        {
            "inputs": {"input": "Explain quantum computing"},
            "outputs": {"response": "Quantum computing uses quantum mechanics principles like superposition and entanglement. Qubits can represent 0 and 1 simultaneously."},
            "expectations": {
                "expected_response": "Quantum computing uses qubits which leverage superposition.",
                "guidelines": [
                    "Must mention superposition",
                    "Must explain qubits",
                    "Keep technical but accessible"
                ]
            }
        },
        {
            "inputs": {"input": "What is machine learning?"},
            "outputs": {"response": "Machine learning trains algorithms on data to make predictions. For example, spam filters learn from email examples."},
            "expectations": {
                "expected_response": "ML trains on data to make predictions.",
                "guidelines": [
                    "Must mention training data",
                    "Must include a real-world example",
                    "Keep simple for beginners"
                ]
            }
        },
        {
            "inputs": {"input": "Describe neural networks"},
            "outputs": {"response": "Neural networks have layers of interconnected nodes that process information, similar to biological neurons."},
            "expectations": {
                "expected_response": "Neural networks process information through layers of nodes.",
                "guidelines": [
                    "Must explain layers",
                    "Must mention nodes or neurons",
                    "Use analogy to biological systems"
                ]
            }
        }
    ]

    optimizer = TurnkeyOptimizer(config_path="config/agent_config.yaml")

    # ExpectationsGuidelines automatically detects and uses per-example guidelines
    results = optimizer.evaluate_agent(
        agent_name="technical_explainer",
        predict_fn=my_agent,
        eval_data=eval_data,
        use_groundedness=False,
        custom_guidelines=None  # ← No global guidelines, using per-example instead
    )

    print(f"\n✅ Per-Example Guidelines Evaluation Complete!")
    print(f"Each example was evaluated against its own specific guidelines")
    print(f"Metrics: {results['metrics']}")


# ============================================================================
# Example 5: Loading Data from Delta Lake
# ============================================================================

def example_delta_lake_evaluation():
    """Load evaluation data from Delta Lake and run evaluation."""

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()

    # Load from Delta table
    df = spark.table("main.agents.evaluation_data")

    # Convert to MLflow 3 format
    eval_data = []
    for row in df.collect():
        eval_data.append({
            "inputs": {
                "input": row.input,
                "context": row.context if hasattr(row, 'context') else None
            },
            "outputs": {
                "response": row.response
            },
            "expectations": {
                "expected_response": row.expected_response
            }
        })

    def my_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Your agent logic
        return {"response": "agent response"}

    optimizer = TurnkeyOptimizer(config_path="config/agent_config.yaml")

    results = optimizer.evaluate_agent(
        agent_name="my_agent",
        predict_fn=my_agent,
        eval_data=eval_data,
        use_groundedness=True
    )

    print(f"✅ Evaluated {results['num_examples']} examples from Delta Lake")
    print(f"Metrics: {results['metrics']}")


# ============================================================================
# Example 5: Viewing Results in MLflow UI
# ============================================================================

def example_view_results():
    """
    After running evaluation, view results in MLflow UI.

    Steps:
    1. Run evaluation (any of the examples above)
    2. Go to Databricks MLflow UI
    3. Navigate to your experiment (e.g., /Users/your-email/agent-evaluations)
    4. Click on the evaluation run
    5. View traces and assessments

    Accessing traces programmatically:
    """
    import mlflow

    # Get the run ID from evaluation results
    run_id = "your-run-id-here"

    # Search traces
    traces = mlflow.search_traces(run_id=run_id)

    print(f"Found {len(traces)} traces")

    # View assessments
    for col in traces.columns:
        if col.startswith("assessments."):
            metric_name = col.replace("assessments.", "")
            values = traces[col].dropna()

            if len(values) > 0:
                # Calculate pass rate for pass/fail metrics
                if values.iloc[0] in ["yes", "no", "pass", "fail"]:
                    pass_count = sum(1 for v in values if v in ["yes", "pass"])
                    pass_rate = pass_count / len(values)
                    print(f"{metric_name}: {pass_rate:.1%} pass rate")
                else:
                    # Average for numeric metrics
                    avg = values.astype(float).mean()
                    print(f"{metric_name}: {avg:.3f} average")


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("MLflow 3 Evaluation Examples")
    print("="*80)

    # Run examples
    print("\n1. Simple Evaluation (Correctness + Relevance)")
    print("-" * 80)
    example_simple_evaluation()

    print("\n\n2. RAG Evaluation (with Groundedness)")
    print("-" * 80)
    example_rag_evaluation()

    print("\n\n3. Custom Guidelines Evaluation")
    print("-" * 80)
    example_custom_guidelines()

    print("\n\n4. Per-Example Guidelines (ExpectationsGuidelines)")
    print("-" * 80)
    example_expectations_guidelines()

    print("\n\n5. Delta Lake Evaluation")
    print("-" * 80)
    # example_delta_lake_evaluation()  # Uncomment if you have Delta table

    print("\n\n6. Viewing Results")
    print("-" * 80)
    print("See function example_view_results() for how to access traces")

    print("\n" + "="*80)
    print("✅ All examples complete!")
    print("="*80)
