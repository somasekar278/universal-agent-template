# Evaluation & Optimization Guide

Complete guide to evaluating and optimizing agents using MLflow 3 and DSPy.

---

## Table of Contents

1. [Philosophy](#philosophy)
2. [MLflow 3 Evaluation](#mlflow-3-evaluation)
3. [Scorer Types](#scorer-types)
4. [Custom Scorers](#custom-scorers)
5. [Custom LLM Judges](#custom-llm-judges)
6. [Benchmarking](#benchmarking)
7. [Prompt Optimization](#prompt-optimization)
8. [On-Demand Optimization](#on-demand-optimization)
9. [Guidelines vs ExpectationsGuidelines](#guidelines-vs-expectationsguidelines)

---

## Philosophy

**BUILD ON TOP OF MLflow 3, not INSTEAD OF MLflow 3.**

This framework uses MLflow 3's native GenAI evaluation APIs. All custom scorers and judges follow MLflow 3 specifications.

---

## MLflow 3 Evaluation

### Basic Evaluation

```python
import mlflow
from mlflow.genai import evaluate
from mlflow.genai.scorers import Correctness, Safety

# Prepare data
eval_data = [
    {
        "inputs": {"input": "What is ML?"},
        "outputs": {"response": "Machine Learning is..."},
        "expectations": {"expected_response": "ML is a subset of AI..."}
    }
]

# Run evaluation
result = evaluate(
    data=eval_data,
    scorers=[Correctness(), Safety()]
)

# View results
print(f"View in MLflow UI: {result.mlflow_ui_url}")
```

### Evaluation with Delta Tables

```python
# Load data from Delta table
dataset = mlflow.data.load_delta(table_name="main.benchmarks.fraud_detection")

# Convert to evaluation format
eval_data = []
for row in dataset.to_pandas().iterrows():
    eval_data.append({
        "inputs": {"input": row["input"]},
        "outputs": {"response": row["output"]},
        "expectations": {"expected_response": row["expected"]}
    })

# Evaluate
result = evaluate(data=eval_data, scorers=[Correctness()])
```

---

## Scorer Types

MLflow 3 supports **4 types** of scorers:

### 1. Built-in Judges (LLM-based)

Pre-built scorers that use LLMs:

```python
from mlflow.genai.scorers import (
    Correctness,           # Checks if response matches expectations
    Groundedness,          # Checks if response is grounded in context
    RelevanceToQuery,      # Checks relevance to input
    Safety,                # Checks for unsafe content
    RetrievalGroundedness, # For RAG: context grounded in retrieved docs
    RetrievalRelevance,    # For RAG: retrieved docs relevant to query
    RetrievalSufficiency,  # For RAG: enough context retrieved
)

# Use them
result = evaluate(
    data=eval_data,
    scorers=[
        Correctness(),
        RelevanceToQuery(),
        Safety()
    ]
)
```

### 2. Guidelines Scorers (LLM-based)

Evaluate against natural language guidelines:

```python
from mlflow.genai.scorers import Guidelines

guidelines = Guidelines(
    guidelines="The response should be professional, concise, and actionable. "
               "It should address the customer's concern directly."
)

result = evaluate(data=eval_data, scorers=[guidelines])
```

### 3. ExpectationsGuidelines (LLM-based)

Like Guidelines, but reads guidelines from data expectations:

```python
from mlflow.genai.scorers import ExpectationsGuidelines

# Data format
eval_data = [
    {
        "inputs": {"input": "Help me"},
        "outputs": {"response": "Here's how..."},
        "expectations": {
            "expected_response": "A helpful response",
            "guidelines": "Be empathetic and provide step-by-step instructions"
        }
    }
]

result = evaluate(
    data=eval_data,
    scorers=[ExpectationsGuidelines()]  # Reads from expectations.guidelines
)
```

### 4. Code-based Scorers (Deterministic)

Custom Python functions using `@scorer` decorator:

```python
from mlflow.genai.scorers import scorer
from mlflow.entities import Feedback

@scorer
def exact_match(
    *,  # All arguments must be keyword-only
    inputs=None,
    outputs=None,
    expectations=None,
    trace=None
) -> Feedback:
    """Check if response exactly matches expected"""
    response = outputs.get("response", "") if isinstance(outputs, dict) else str(outputs)
    expected = expectations.get("expected_response", "")

    matches = response.strip() == expected.strip()

    return Feedback(
        value="yes" if matches else "no",
        rationale=f"Response {'matches' if matches else 'does not match'} expected output"
    )

# Use it
result = evaluate(data=eval_data, scorers=[exact_match])
```

**See:** `evaluation/custom_scorers.py` for 15+ pre-built code-based scorers

---

## Custom Scorers

### Creating Custom Code-Based Scorers

All custom scorers must follow this signature:

```python
from mlflow.genai.scorers import scorer
from mlflow.entities import Feedback
from typing import Optional, Dict, Any

@scorer
def my_custom_scorer(
    *,  # REQUIRED: Forces keyword-only arguments
    inputs: Optional[Dict[str, Any]] = None,
    outputs: Optional[Any] = None,
    expectations: Optional[Dict[str, Any]] = None,
    trace: Optional[Any] = None
) -> Feedback:
    """
    Your scorer logic.

    Returns:
        Feedback with value and rationale
    """
    # Your logic here
    return Feedback(
        value="yes",  # or "no", or numeric score
        rationale="Explanation of the score"
    )
```

### Examples

**Contains Keywords:**
```python
@scorer
def contains_keywords(
    *,
    inputs=None,
    outputs=None,
    expectations=None,
    trace=None
) -> Feedback:
    """Check if response contains required keywords"""
    response = outputs.get("response", "") if isinstance(outputs, dict) else str(outputs)
    keywords = expectations.get("required_keywords", [])

    found = [kw for kw in keywords if kw.lower() in response.lower()]
    all_found = len(found) == len(keywords)

    return Feedback(
        value="yes" if all_found else "no",
        rationale=f"Found {len(found)}/{len(keywords)} required keywords: {found}"
    )
```

**Latency Check:**
```python
@scorer
def latency_check(
    *,
    inputs=None,
    outputs=None,
    expectations=None,
    trace=None
) -> Feedback:
    """Check if response latency is acceptable"""
    if trace and hasattr(trace, 'execution_time_ms'):
        latency = trace.execution_time_ms
    else:
        latency = outputs.get("latency_ms", 0) if isinstance(outputs, dict) else 0

    threshold = expectations.get("max_latency_ms", 1000)
    within_threshold = latency <= threshold

    return Feedback(
        value="yes" if within_threshold else "no",
        rationale=f"Latency {latency}ms {'<=' if within_threshold else '>'} threshold {threshold}ms"
    )
```

**See:** `evaluation/custom_scorers.py` for 15+ more examples

---

## Custom LLM Judges

For complex, subjective evaluation that requires LLM reasoning.

### Creating Custom Judges

```python
from mlflow.genai.judges import make_judge
from typing import Literal

# Define judge with natural language instructions
issue_resolution_judge = make_judge(
    name="issue_resolution",
    instructions=(
        "Evaluate if the customer's issue was fully resolved in the conversation.\n\n"
        "User's messages: {{ inputs.messages }}\n"
        "Agent's responses: {{ outputs.messages }}"
    ),
    feedback_value_type=Literal["fully_resolved", "partially_resolved", "needs_follow_up"],
    model="databricks:/databricks-llama-3-70b-instruct"
)

# Use it
result = evaluate(data=eval_data, scorers=[issue_resolution_judge])
```

### Examples

**Technical Accuracy:**
```python
technical_accuracy_judge = make_judge(
    name="technical_accuracy",
    instructions=(
        "Evaluate the technical accuracy of the response.\n\n"
        "Input: {{ inputs.input }}\n"
        "Response: {{ outputs.response }}\n"
        "Expected: {{ expectations.expected_response }}"
    ),
    feedback_value_type=Literal["accurate", "partially_accurate", "inaccurate"],
    model="databricks:/databricks-llama-3-70b-instruct"
)
```

**Empathy Check:**
```python
empathy_judge = make_judge(
    name="empathy",
    instructions=(
        "Evaluate if the agent response shows empathy and understanding.\n\n"
        "Customer message: {{ inputs.input }}\n"
        "Agent response: {{ outputs.response }}"
    ),
    feedback_value_type=Literal["highly_empathetic", "somewhat_empathetic", "not_empathetic"],
    model="databricks:/databricks-dbrx-instruct"
)
```

**See:** `evaluation/custom_judges.py` for 10+ pre-built judges

---

## Benchmarking

### Using CLI

```bash
# Run benchmark on Delta table
agent-benchmark \
    --dataset main.benchmarks.fraud_detection \
    --experiment /benchmarks/fraud \
    --name "fraud_detector_v1"

# View results in MLflow UI
```

### Using Python

```python
from evaluation.mlflow_benchmark import MLflowBenchmark
from evaluation.custom_scorers import exact_match, latency_check
from evaluation.custom_judges import technical_accuracy_judge

benchmark = MLflowBenchmark()

result = benchmark.run_benchmark(
    dataset_table="main.benchmarks.fraud_detection",
    scorers=[
        Correctness(),
        Safety(),
        exact_match,
        latency_check,
        technical_accuracy_judge
    ],
    experiment_name="/benchmarks/fraud",
    run_name="fraud_detector_v2",
    tags={"agent": "fraud_detector", "version": "2.0"}
)

print(f"View results: {result.mlflow_ui_url}")
```

### Comparing Runs

Use MLflow UI:
1. Navigate to experiment
2. Select multiple runs
3. Click "Compare"
4. View side-by-side metrics, params, charts

---

## Prompt Optimization

### Turnkey Optimization

Configure in `config/agent_config.yaml`:

```yaml
optimization:
  agents:
    fraud_detector:
      enabled: true
      dataset: "main.agents.fraud_training_data"

      dspy:
        enabled: true
        optimizer: "BootstrapFewShot"
        max_demos: 5

      textgrad:
        enabled: true
        iterations: 10
        learning_rate: 0.1

      save_to_uc: true
      uc_path: "main.agents.optimized_prompts"
```

### Run Optimization

```bash
# CLI
agent-optimize --config config/optimization/fraud_detector.yaml

# Or specify inline
agent-optimize \
    --agent fraud_detector \
    --dataset main.agents.fraud_training_data \
    --optimizer BootstrapFewShot
```

### Results

Optimization results are saved to:
- **MLflow:** Experiment tracking, metrics
- **Unity Catalog:** Optimized prompt versions

Access via:
```python
# Load optimized prompt from UC
prompt = mlflow.load_model(f"models:/fraud_detector_prompt/production")
```

---

## On-Demand Optimization

Agents can trigger their own optimization based on performance.

### Self-Monitoring Agent

```python
from mcp import McpClient

async with McpClient() as client:
    # Check performance
    perf = await client.call_databricks_tool(
        "check_performance",
        {"agent_id": "fraud_detector"}
    )

    if perf["status"] == "degraded":
        # Trigger optimization
        opt_result = await client.call_databricks_tool(
            "trigger_optimization",
            {"agent_id": "fraud_detector"}
        )

        opt_id = opt_result["optimization_id"]

        # Monitor optimization status
        while True:
            status = await client.call_databricks_tool(
                "check_optimization_status",
                {"optimization_id": opt_id}
            )

            if status["status"] in ["completed", "failed"]:
                break

            await asyncio.sleep(30)
```

### Supervisory Monitoring Service

Configure in `config/agent_config.yaml`:

```yaml
self_improvement_service:
  enabled: true
  check_interval_seconds: 300  # Check every 5 minutes

  agents:
    fraud_detector:
      enabled: true
      thresholds:
        accuracy: 0.90
        error_rate: 0.03
        latency: 1.0
      cooldown_hours: 24

      optimization:
        config_path: "config/optimization/fraud_detector.yaml"
```

The service runs as a background task and automatically:
1. Monitors agent performance
2. Detects degradation
3. Triggers optimization
4. Sends notifications

**See:** `sota_agent/self_improvement_service.py`

---

## Guidelines vs ExpectationsGuidelines

### Guidelines

**Use when:** Same guidelines for all examples

```python
from mlflow.genai.scorers import Guidelines

guidelines = Guidelines(
    guidelines="Responses should be professional and concise."
)

result = evaluate(data=eval_data, scorers=[guidelines])
```

### ExpectationsGuidelines

**Use when:** Different guidelines per example

```python
from mlflow.genai.scorers import ExpectationsGuidelines

eval_data = [
    {
        "inputs": {"input": "Angry customer"},
        "outputs": {"response": "..."},
        "expectations": {
            "guidelines": "Be empathetic and de-escalate"
        }
    },
    {
        "inputs": {"input": "Technical question"},
        "outputs": {"response": "..."},
        "expectations": {
            "guidelines": "Be precise and technical"
        }
    }
]

result = evaluate(
    data=eval_data,
    scorers=[ExpectationsGuidelines()]  # Reads from each example
)
```

---

## Quick Reference

### Scorer Selection Guide

| Need | Use | Example |
|------|-----|---------|
| Basic correctness | `Correctness()` | Built-in |
| Safety check | `Safety()` | Built-in |
| RAG evaluation | `RetrievalGroundedness()` | Built-in |
| Same guidelines for all | `Guidelines()` | Built-in |
| Different guidelines per example | `ExpectationsGuidelines()` | Built-in |
| Simple rule (fast) | Custom `@scorer` | `exact_match` |
| Complex subjective | Custom judge | `empathy_judge` |

### Combining Scorers

```python
from mlflow.genai.scorers import Correctness, Safety
from evaluation.custom_scorers import latency_check, forbidden_terms
from evaluation.custom_judges import empathy_judge

result = evaluate(
    data=eval_data,
    scorers=[
        # Built-in
        Correctness(),
        Safety(),

        # Custom code-based
        latency_check,
        forbidden_terms,

        # Custom LLM judge
        empathy_judge
    ]
)
```

### Configuration Files

- **Agent Config:** `config/agent_config.yaml`
- **Optimization Config:** `config/optimization/<agent>.yaml`
- **Custom Scorers:** `evaluation/custom_scorers.py`
- **Custom Judges:** `evaluation/custom_judges.py`

---

## Getting Help

- **Platform Integration:** `PLATFORM_INTEGRATION.md`
- **Monitoring:** `OBSERVABILITY_GUIDE.md`
- **Migration:** `MIGRATION_GUIDE_V0.5.md`

---

**Remember: Build ON TOP OF MLflow 3, not INSTEAD OF MLflow 3.**
