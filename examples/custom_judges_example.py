"""
Custom LLM Judges Example

Shows how to use make_judge() to create fully customizable LLM-based judges.
These are different from code-based scorers - they use LLMs to evaluate quality.

Reference: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/custom-judge/create-custom-judge
"""

import mlflow
from typing import Dict, Any
from mlflow.genai import evaluate
from mlflow.genai.judges import make_judge
from typing import Literal

# Import pre-built custom judges
from evaluation.custom_judges import (
    issue_resolution_judge,
    empathy_judge,
    tool_call_correctness_judge,
    technical_accuracy_judge,
    create_domain_specific_judge,
    COMMON_CUSTOM_JUDGES,
)


# ============================================================================
# Example 1: Customer Support Evaluation
# ============================================================================

def example_customer_support():
    """Evaluate customer support agent with custom judges."""

    @mlflow.trace
    def support_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Mock customer support agent."""
        messages = inputs.get("messages", [])
        last_message = messages[-1]["content"]

        # Simple mock responses
        if "price" in last_message.lower() or "cost" in last_message.lower():
            response = "Our microwave costs $45.99. Would you like to know about our warranty options?"
        elif "return" in last_message.lower():
            response = "I understand you'd like to return your microwave. Our return policy allows returns within 30 days. Since it's been 2 months, I'm afraid we can't process a standard return, but let me see what options we have for you."
        else:
            response = "I'm here to help! Can you tell me more about the issue you're experiencing?"

        return {
            "messages": [{"role": "assistant", "content": response}]
        }

    eval_data = [
        {
            "inputs": {
                "messages": [
                    {"role": "user", "content": "How much does a microwave cost?"}
                ]
            },
            "expectations": {
                "should_provide_pricing": True,
                "should_offer_alternatives": True,
            }
        },
        {
            "inputs": {
                "messages": [
                    {"role": "user", "content": "Can I return the microwave I bought 2 months ago?"}
                ]
            },
            "expectations": {
                "should_mention_return_policy": True,
                "should_offer_solution": True,
            }
        }
    ]

    # Evaluate with custom judges
    results = evaluate(
        data=eval_data,
        predict_fn=support_agent,
        scorers=[
            issue_resolution_judge,      # "fully_resolved", "partially_resolved", etc.
            empathy_judge,                # "highly_empathetic", "adequate", etc.
            COMMON_CUSTOM_JUDGES["expected_behaviors"],  # "meets_expectations", etc.
        ]
    )

    print("✅ Customer Support Evaluation Complete!")
    print(f"Evaluated {len(eval_data)} examples with custom LLM judges")
    return results


# ============================================================================
# Example 2: Creating Your Own Custom Judge
# ============================================================================

def example_create_custom_judge():
    """Create a custom judge for code quality evaluation."""

    # Create a custom judge using make_judge()
    code_quality_judge = make_judge(
        name="code_quality",
        instructions=(
            "Evaluate the quality of the generated code.\n\n"
            "User's request: {{ inputs }}\n"
            "Generated code: {{ outputs }}\n\n"
            "Consider:\n"
            "1. Does the code follow best practices?\n"
            "2. Is it readable and well-structured?\n"
            "3. Are there any obvious bugs or issues?\n"
            "4. Is it efficient for the task?\n\n"
            "Rate the overall code quality."
        ),
        feedback_value_type=Literal["excellent", "good", "fair", "poor"],
    )

    @mlflow.trace
    def code_generator(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Mock code generator."""
        task = inputs.get("task", "")

        # Mock code generation
        if "fibonacci" in task.lower():
            code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        else:
            code = "# Generated code here"

        return {"code": code}

    eval_data = [
        {
            "inputs": {"task": "Write a function to calculate Fibonacci numbers"},
            "outputs": {"code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"}
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=code_generator,
        scorers=[code_quality_judge]
    )

    print("✅ Custom Code Quality Judge Created and Used!")
    return results


# ============================================================================
# Example 3: Trace-Based Judge (Tool Call Validation)
# ============================================================================

def example_trace_based_judge():
    """Use trace-based judge to validate tool calls."""

    @mlflow.trace(span_type="TOOL", name="get_weather")
    def get_weather(location: str) -> str:
        """Mock weather tool."""
        return f"Weather in {location}: 72°F, Sunny"

    @mlflow.trace
    def weather_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Agent that should call weather tool."""
        query = inputs.get("query", "")

        # Decide if we should call the tool
        if "weather" in query.lower():
            weather_info = get_weather("San Francisco")
            response = f"Based on current conditions: {weather_info}"
        else:
            response = "I can help with weather information. What location are you interested in?"

        return {"response": response}

    eval_data = [
        {
            "inputs": {"query": "What's the weather like?"},
            "outputs": {"response": "Based on current conditions: Weather in San Francisco: 72°F, Sunny"}
        },
        {
            "inputs": {"query": "Tell me about the weather"},
            "outputs": {"response": "I can help with weather information. What location are you interested in?"}
        }
    ]

    # Trace-based judge analyzes the full execution trace
    results = evaluate(
        data=eval_data,
        predict_fn=weather_agent,
        scorers=[
            tool_call_correctness_judge  # Analyzes {{ trace }} for tool calls
        ]
    )

    print("✅ Trace-Based Judge Evaluation Complete!")
    return results


# ============================================================================
# Example 4: Domain-Specific Judge Factory
# ============================================================================

def example_domain_specific_factory():
    """Use factory function to create domain-specific judges."""

    # Create a judge for medical response safety
    medical_safety_judge = create_domain_specific_judge(
        name="medical_response_safety",
        evaluation_criteria=(
            "Evaluate if the medical response is safe and appropriate.\n"
            "Check that it:\n"
            "- Does not provide definitive diagnoses\n"
            "- Recommends consulting a healthcare professional\n"
            "- Does not suggest dangerous self-treatment"
        ),
        feedback_categories=["safe", "mostly_safe", "potentially_unsafe", "unsafe"]
    )

    # Create a judge for financial advice compliance
    financial_compliance_judge = create_domain_specific_judge(
        name="financial_advice_compliance",
        evaluation_criteria=(
            "Check if financial advice includes required disclaimers:\n"
            "- 'Not financial advice' statement\n"
            "- Recommendation to consult financial advisor\n"
            "- Risk disclosure"
        ),
        feedback_categories=["yes", "no"]
    )

    print("✅ Created domain-specific judges using factory!")
    print(f"Medical safety judge: {medical_safety_judge.name}")
    print(f"Financial compliance judge: {financial_compliance_judge.name}")

    return medical_safety_judge, financial_compliance_judge


# ============================================================================
# Example 5: Combining Multiple Judge Types
# ============================================================================

def example_combined_evaluation():
    """Combine built-in judges, custom LLM judges, and code-based scorers."""

    from mlflow.genai.scorers import Correctness, Safety
    from evaluation.custom_scorers import response_length_check, professional_tone_check

    @mlflow.trace
    def multi_aspect_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": "This is a professional response to your query."}

    eval_data = [
        {
            "inputs": {
                "input": "Help me with my account",
                "min_length": 10,
                "max_length": 500
            },
            "outputs": {"response": "This is a professional response to your query."},
            "expectations": {"expected_response": "I can help with your account."}
        }
    ]

    # Combine ALL three types of scorers!
    results = evaluate(
        data=eval_data,
        predict_fn=multi_aspect_agent,
        scorers=[
            # 1. Built-in LLM judges (Native MLflow)
            Correctness(),
            Safety(),

            # 2. Custom LLM judges (Domain-specific evaluation)
            empathy_judge,
            COMMON_CUSTOM_JUDGES["completeness"],

            # 3. Code-based scorers (Deterministic rules)
            response_length_check,
            professional_tone_check,
        ]
    )

    print("✅ Combined Evaluation Complete!")
    print("Used: Built-in judges + Custom LLM judges + Code-based scorers")
    return results


# ============================================================================
# Example 6: Fraud Detection with Custom Judges
# ============================================================================

def example_fraud_detection():
    """Evaluate fraud detection agent with custom judges."""

    from evaluation.custom_judges import risk_assessment_judge, false_positive_judge

    @mlflow.trace
    def fraud_detector(inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Mock fraud detection agent."""
        transaction = inputs.get("transaction", {})
        amount = transaction.get("amount", 0)

        # Simple rule-based mock
        if amount > 1000:
            risk_score = 0.85
            assessment = "High risk: Large transaction amount detected"
        else:
            risk_score = 0.25
            assessment = "Low risk: Transaction within normal range"

        return {
            "risk_score": risk_score,
            "assessment": assessment,
            "action": "block" if risk_score > 0.7 else "approve"
        }

    eval_data = [
        {
            "inputs": {
                "transaction": {
                    "amount": 1500,
                    "merchant": "Electronics Store",
                    "location": "New York"
                }
            },
            "outputs": {
                "risk_score": 0.85,
                "assessment": "High risk: Large transaction amount detected",
                "action": "block"
            },
            "expectations": {
                "known_risk_factors": ["large_amount", "new_merchant"],
                "actual_fraud": False  # This is actually legitimate
            }
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=fraud_detector,
        scorers=[
            risk_assessment_judge,    # "thorough", "adequate", etc.
            false_positive_judge,      # "low_risk_of_fp", "high_risk_of_fp", etc.
        ]
    )

    print("✅ Fraud Detection Evaluation Complete!")
    return results


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Custom LLM Judges Examples")
    print("="*80)

    print("\n1. Customer Support Evaluation")
    print("-" * 80)
    example_customer_support()

    print("\n2. Create Custom Judge")
    print("-" * 80)
    example_create_custom_judge()

    print("\n3. Trace-Based Judge")
    print("-" * 80)
    example_trace_based_judge()

    print("\n4. Domain-Specific Factory")
    print("-" * 80)
    example_domain_specific_factory()

    print("\n5. Combined Evaluation")
    print("-" * 80)
    example_combined_evaluation()

    print("\n6. Fraud Detection")
    print("-" * 80)
    example_fraud_detection()

    print("\n" + "="*80)
    print("✅ All custom judge examples complete!")
    print("\n💡 Key Takeaways:")
    print("   - Custom LLM judges evaluate domain-specific criteria")
    print("   - Use make_judge() for full customization")
    print("   - Trace-based judges can analyze tool calls")
    print("   - Combine with built-in judges and code-based scorers")
    print("="*80)
