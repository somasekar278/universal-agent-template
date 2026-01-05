"""
Custom Scorers Example - Rule-Based Evaluation with MLflow 3

Shows how to use custom rule-based scorers alongside LLM judges.
Rule-based scorers are:
- ✅ Fast (no LLM calls)
- ✅ Deterministic (same input = same output)
- ✅ Cost-effective (no API costs)
- ✅ Domain-specific (your business rules)

Perfect for:
- Format validation
- Compliance checks
- Performance thresholds
- Business logic validation
"""

from typing import Dict, Any
from mlflow.genai import evaluate
from mlflow.genai.scorers import Correctness, Safety  # LLM-based scorers
from evaluation.custom_scorers import (
    # String matching
    exact_match,
    contains_keywords,
    forbidden_terms,

    # Format checks
    response_length_check,
    word_count_check,
    json_format_check,

    # Regex patterns
    regex_pattern_match,
    email_format_check,
    url_format_check,

    # Numeric thresholds
    confidence_threshold,
    latency_check,

    # Domain-specific
    fraud_score_threshold,
    medical_disclaimer_check,
    positive_tone_check,
    professional_tone_check,

    # Comprehensive
    comprehensive_quality_check,

    # Factory
    create_custom_scorer
)


# ============================================================================
# Example 1: Basic Rule-Based Scoring
# ============================================================================

def example_basic_rule_based():
    """Use rule-based scorers only (no LLM calls)."""

    def my_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("input", "")
        return {"response": f"Thank you for your question about {query}. I'm happy to help!"}

    eval_data = [
        {
            "inputs": {
                "input": "What is your return policy?",
                "min_length": 20,
                "max_length": 200,
                "required_keywords": ["thank", "help"]
            },
            "outputs": {
                "response": "Thank you for asking. I'm happy to help with our return policy."
            },
            "expectations": {
                "expected_response": "Thank you for asking. I'm happy to help with our return policy."
            }
        }
    ]

    # Use only rule-based scorers (fast, no LLM costs!)
    results = evaluate(
        data=eval_data,
        predict_fn=my_agent,
        scorers=[
            exact_match,              # Exact string match
            response_length_check,    # Length validation
            contains_keywords,        # Required keywords
            positive_tone_check,      # Positive language
            professional_tone_check   # Professional tone
        ]
    )

    print("✅ Evaluation complete (no LLM calls!)")
    return results


# ============================================================================
# Example 2: Hybrid Scoring (Rule-Based + LLM Judges)
# ============================================================================

def example_hybrid_scoring():
    """Combine fast rule-based checks with deep LLM evaluation."""

    def my_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": "I can help you with that."}

    eval_data = [
        {
            "inputs": {
                "input": "Help me",
                "min_length": 10,
                "max_length": 500
            },
            "outputs": {
                "response": "I can help you with that. What do you need?"
            },
            "expectations": {
                "expected_response": "I can assist you. What do you need help with?"
            }
        }
    ]

    # Combine both types of scorers
    results = evaluate(
        data=eval_data,
        predict_fn=my_agent,
        scorers=[
            # Fast rule-based checks (run first, no cost)
            response_length_check,
            professional_tone_check,

            # Deep LLM evaluation (run after basic checks pass)
            Correctness(),  # ← LLM-based (costs $)
            Safety()        # ← LLM-based (costs $)
        ]
    )

    print("✅ Hybrid evaluation complete")
    return results


# ============================================================================
# Example 3: Domain-Specific Rules (Fraud Detection)
# ============================================================================

def example_fraud_detection():
    """Domain-specific: Fraud detection with business rules."""

    def fraud_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Your fraud detection logic
        return {
            "response": "This transaction appears fraudulent.",
            "fraud_score": 0.85,
            "action": "block",
            "confidence": 0.92
        }

    eval_data = [
        {
            "inputs": {
                "input": "Check transaction TXN123",
                "min_confidence": 0.8
            },
            "outputs": {
                "response": "This transaction appears fraudulent.",
                "fraud_score": 0.85,
                "action": "block",
                "confidence": 0.92
            },
            "expectations": {
                "expected_response": "Transaction flagged as fraudulent."
            }
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=fraud_agent,
        scorers=[
            # Business logic validation
            fraud_score_threshold,  # Checks if score matches action
            confidence_threshold,   # Ensures confidence > 0.8

            # LLM evaluation
            Correctness()
        ]
    )

    print("✅ Fraud detection evaluation complete")
    return results


# ============================================================================
# Example 4: Compliance Checking (Medical/Financial)
# ============================================================================

def example_compliance_check():
    """Check for required disclaimers in regulated domains."""

    def medical_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "response": "For headaches, rest is helpful. However, please consult your physician for persistent symptoms."
        }

    eval_data = [
        {
            "inputs": {"input": "What should I do for headaches?"},
            "outputs": {
                "response": "For headaches, rest is helpful. However, please consult your physician for persistent symptoms."
            },
            "expectations": {
                "expected_response": "Rest can help. Consult a doctor for persistent headaches."
            }
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=medical_agent,
        scorers=[
            medical_disclaimer_check,  # ✅ Ensures medical disclaimer present
            professional_tone_check,
            Correctness(),
            Safety()
        ]
    )

    print("✅ Compliance check complete")
    return results


# ============================================================================
# Example 5: Format Validation (Structured Outputs)
# ============================================================================

def example_format_validation():
    """Validate structured outputs (JSON, email, URL formats)."""

    def structured_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "response": '{"status": "success", "email": "user@example.com", "url": "https://example.com"}'
        }

    eval_data = [
        {
            "inputs": {"input": "Get user info"},
            "outputs": {
                "response": '{"status": "success", "email": "user@example.com"}'
            },
            "expectations": {}
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=structured_agent,
        scorers=[
            json_format_check,   # ✅ Validates JSON structure
            email_format_check,  # ✅ Validates email format
            url_format_check     # ✅ Validates URL format (if present)
        ]
    )

    print("✅ Format validation complete")
    return results


# ============================================================================
# Example 6: Performance Validation (Latency)
# ============================================================================

def example_performance_check():
    """Check if agent meets performance requirements."""

    def fast_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "response": "Quick response",
            "latency_ms": 150
        }

    eval_data = [
        {
            "inputs": {
                "input": "Quick question",
                "max_latency_ms": 500
            },
            "outputs": {
                "response": "Quick response",
                "latency_ms": 150
            },
            "expectations": {}
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=fast_agent,
        scorers=[
            latency_check,  # ✅ Ensures response within 500ms
            response_length_check
        ]
    )

    print("✅ Performance check complete")
    return results


# ============================================================================
# Example 7: Custom Scorer Factory
# ============================================================================

def example_custom_scorer_factory():
    """Create your own custom scorers on the fly."""

    # Define custom check logic
    def check_contains_apology(inputs, outputs, expectations):
        """Check if customer service response includes apology."""
        response = outputs.get("response", "").lower()
        apology_words = ["sorry", "apologize", "regret", "unfortunately"]
        has_apology = any(word in response for word in apology_words)
        return "yes" if has_apology else "no"

    def check_provides_next_steps(inputs, outputs, expectations):
        """Check if response provides clear next steps."""
        response = outputs.get("response", "").lower()
        action_words = ["will", "can", "next", "follow up", "contact", "send"]
        has_action = any(word in response for word in action_words)
        return "yes" if has_action else "no"

    # Create scorers using factory
    apology_scorer = create_custom_scorer(
        name="contains_apology",
        check_function=check_contains_apology,
        description="Checks if customer service response includes apology"
    )

    next_steps_scorer = create_custom_scorer(
        name="provides_next_steps",
        check_function=check_provides_next_steps,
        description="Checks if response provides actionable next steps"
    )

    def support_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "response": "I apologize for the inconvenience. I will look into this and contact you within 24 hours."
        }

    eval_data = [
        {
            "inputs": {"input": "My order is late"},
            "outputs": {
                "response": "I apologize for the inconvenience. I will look into this and contact you within 24 hours."
            },
            "expectations": {}
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=support_agent,
        scorers=[
            apology_scorer,      # ✅ Custom: checks for apology
            next_steps_scorer,   # ✅ Custom: checks for next steps
            positive_tone_check,
            professional_tone_check
        ]
    )

    print("✅ Custom scorer evaluation complete")
    return results


# ============================================================================
# Example 8: Comprehensive Quality Gate
# ============================================================================

def example_quality_gate():
    """Use comprehensive check as a quality gate."""

    def production_agent(inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "response": "Thank you for your question. I'm happy to provide information about our services."
        }

    eval_data = [
        {
            "inputs": {"input": "Tell me about your services"},
            "outputs": {
                "response": "Thank you for your question. I'm happy to provide information about our services."
            },
            "expectations": {
                "expected_response": "We offer comprehensive services."
            }
        }
    ]

    results = evaluate(
        data=eval_data,
        predict_fn=production_agent,
        scorers=[
            # Single comprehensive check (combines multiple rules)
            comprehensive_quality_check,  # ✅ Length + tone + forbidden terms

            # Additional specific checks
            positive_tone_check,

            # Final LLM validation
            Correctness(),
            Safety()
        ]
    )

    print("✅ Quality gate evaluation complete")
    return results


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("Custom Scorers Examples (Rule-Based + LLM Hybrid)")
    print("="*80)

    print("\n1. Basic Rule-Based Scoring (No LLM calls)")
    print("-" * 80)
    example_basic_rule_based()

    print("\n2. Hybrid Scoring (Rule-Based + LLM)")
    print("-" * 80)
    example_hybrid_scoring()

    print("\n3. Domain-Specific: Fraud Detection")
    print("-" * 80)
    example_fraud_detection()

    print("\n4. Compliance Checking (Medical/Financial)")
    print("-" * 80)
    example_compliance_check()

    print("\n5. Format Validation (JSON, Email, URL)")
    print("-" * 80)
    example_format_validation()

    print("\n6. Performance Check (Latency)")
    print("-" * 80)
    example_performance_check()

    print("\n7. Custom Scorer Factory")
    print("-" * 80)
    example_custom_scorer_factory()

    print("\n8. Comprehensive Quality Gate")
    print("-" * 80)
    example_quality_gate()

    print("\n" + "="*80)
    print("✅ All examples complete!")
    print("\n💡 Key Takeaway:")
    print("   - Rule-based scorers: Fast, deterministic, no cost")
    print("   - LLM scorers: Deep understanding, semantic evaluation")
    print("   - Best practice: Use both! Rule-based for gates, LLM for quality")
    print("="*80)
