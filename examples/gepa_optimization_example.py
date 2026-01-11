"""
GEPA Optimization Example

Demonstrates how to optimize L1 chatbot prompts using GEPA.
Run this after deploying L1 to see prompt improvement in action.
"""

import mlflow
from mlflow.deployments import get_deploy_client
from optimization.prompt_optimizer import PromptOptimizer


def main():
    """Run GEPA optimization example."""

    print("=" * 60)
    print("GEPA Prompt Optimization Example")
    print("=" * 60)
    print()

    # Step 1: Register initial prompt
    print("📝 Step 1: Registering initial prompt...")

    initial_template = "You are a helpful assistant. Answer the question concisely."

    prompt = mlflow.genai.register_prompt(
        name="l1_demo_prompt",
        template=initial_template
    )

    print(f"✅ Registered: {prompt.uri}")
    print(f"   Template: {initial_template}")
    print()

    # Step 2: Define agent function
    print("🤖 Step 2: Defining agent function...")

    def l1_agent(question: str) -> str:
        """Simple L1 agent using registered prompt."""
        prompt = mlflow.genai.load_prompt("prompts:/l1_demo_prompt@latest")

        client = get_deploy_client("databricks")
        response = client.predict(
            endpoint="databricks-claude-sonnet-4",
            inputs={
                "messages": [
                    {"role": "system", "content": prompt.template},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.7,
                "max_tokens": 200
            }
        )

        return response["choices"][0]["message"]["content"]

    print("✅ Agent defined")
    print()

    # Step 3: Prepare training data
    print("📊 Step 3: Preparing training data...")

    train_data = [
        {
            "inputs": {"question": "What is 2+2?"},
            "expectations": {"expected_response": "4"}
        },
        {
            "inputs": {"question": "What's the capital of France?"},
            "expectations": {"expected_response": "Paris"}
        },
        {
            "inputs": {"question": "Who wrote Romeo and Juliet?"},
            "expectations": {"expected_response": "William Shakespeare"}
        },
        {
            "inputs": {"question": "What's the largest planet?"},
            "expectations": {"expected_response": "Jupiter"}
        },
        {
            "inputs": {"question": "What year did WW2 end?"},
            "expectations": {"expected_response": "1945"}
        },
    ]

    print(f"✅ Prepared {len(train_data)} training examples")
    print()

    # Step 4: Test baseline performance
    print("🧪 Step 4: Testing baseline performance...")

    sample_question = "What is 2+2?"
    baseline_response = l1_agent(sample_question)

    print(f"   Q: {sample_question}")
    print(f"   A: {baseline_response}")
    print()

    # Step 5: Optimize with GEPA
    print("🔧 Step 5: Optimizing with GEPA...")
    print("   This may take a few minutes...")
    print()

    optimizer = PromptOptimizer(
        gepa_reflection_model="databricks-claude-sonnet-4",
        gepa_max_calls=50  # Lower for demo
    )

    result = optimizer.optimize_with_gepa(
        predict_fn=lambda inputs: l1_agent(inputs["question"]),
        train_data=train_data,
        prompt_uris=[prompt.uri],
        scorers=["correctness"]
    )

    # Step 6: Show results
    print()
    print("=" * 60)
    print("OPTIMIZATION RESULTS")
    print("=" * 60)
    print()

    optimized_prompt = result.optimized_prompts[0]

    print(f"📈 Initial Score: {result.initial_score:.3f}")
    print(f"📈 Final Score: {result.final_score:.3f}")
    if result.improvement:
        print(f"📈 Improvement: {result.improvement:.2%}")
    print()

    print("📝 Original Template:")
    print(f"   {initial_template}")
    print()

    print("✨ Optimized Template:")
    print(f"   {optimized_prompt.template}")
    print()

    print(f"🔗 Optimized Prompt URI: {optimized_prompt.uri}")
    print()

    # Step 7: Test optimized performance
    print("🧪 Step 7: Testing optimized performance...")

    optimized_response = l1_agent(sample_question)

    print(f"   Q: {sample_question}")
    print(f"   A: {optimized_response}")
    print()

    print("=" * 60)
    print("✅ OPTIMIZATION COMPLETE!")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"1. Update your L1 agent to use: {optimized_prompt.uri}")
    print("2. Deploy and test in production")
    print("3. Collect more data and iterate")
    print()


if __name__ == "__main__":
    # Set MLflow tracking
    mlflow.set_tracking_uri("databricks")
    mlflow.set_experiment("/Shared/gepa_optimization_demo")

    try:
        main()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
