

# Human Feedback → Optimized Prompts

**Direct path from SME corrections to optimized prompts (without judges).**

---

## ⚠️ **IMPORTANT: Corrections vs. Ratings**

This optimizer requires **SME CORRECTIONS**, not just ratings!

### **Valid Optimization Paths:**

1. **SME Corrections → GEPA** ✅ (use this optimizer)
   - SMEs provide corrected outputs
   - GEPA has ground truth to optimize towards
   - No judge needed!

2. **SME Ratings → Align Judges → GEPA** ✅ (use Databricks Align Judges)
   - SMEs only provide ratings ("excellent", "poor")
   - Must train a judge from ratings first
   - Use aligned judge to score outputs for GEPA
   - See: https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges

3. **SME Ratings → GEPA** ❌ NOT POSSIBLE
   - Ratings alone don't provide ground truth
   - Must either have corrections OR align a judge

---

## 🎯 **The Problem This Solves**

### **With SME Corrections:**

```
Production Agent → Output
        ↓
    SME Correction → Ground Truth
        ↓
    GEPA → Optimized Prompt  ✅ Direct path!
```

### **With Only SME Ratings:**

```
Production Agent → Output
        ↓
    SME Rating → Need Aligned Judge
        ↓
    Align Judge (https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges)
        ↓
    Aligned Judge → Scores
        ↓
    GEPA → Optimized Prompt
```

### **Our Solution (Simple)**

```
Production Agent → Output
        ↓
    SME Feedback → HumanFeedbackOptimizer → Optimized Prompt ✅
```

**Benefits:**
- ✅ Direct SME feedback to prompts
- ✅ No judge dependency
- ✅ One-step optimization
- ✅ Works with any feedback format

---

## 🚀 **Quick Start**

### **Scenario: SMEs Review Production Outputs**

```python
from optimization import HumanFeedbackOptimizer
import mlflow

# Your agent function
def my_agent(question: str) -> str:
    prompt = mlflow.genai.load_prompt("prompts:/qa/1")
    return llm.call(prompt.format(question=question))

# SME feedback from production
feedback = [
    {
        "inputs": {"question": "What is AI?"},
        "outputs": {"answer": "AI is computers that think"},
        "human_assessment": "poor",
        "corrected_output": "AI (Artificial Intelligence) is the simulation of human intelligence by machines..."
    },
    {
        "inputs": {"question": "What is ML?"},
        "outputs": {"answer": "ML is machine learning"},
        "human_assessment": "fair",
        "corrected_output": "ML (Machine Learning) is a subset of AI that enables systems to learn from data..."
    },
    {
        "inputs": {"question": "What is deep learning?"},
        "outputs": {"answer": "Deep learning uses neural networks..."},
        "human_assessment": "excellent",
        # No correction needed!
    },
]

# Optimize directly from SME feedback
optimizer = HumanFeedbackOptimizer()

result = optimizer.optimize_from_feedback(
    predict_fn=lambda inputs: my_agent(inputs["question"]),
    feedback=feedback,
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="corrected",  # Use SME corrections
    scorers=["correctness"]
)

print(f"Optimized! Improvement: {result.improvement:.2%}")
```

---

## 📊 **Three Feedback Strategies**

### **1. "corrected" - Use SME Corrections (Recommended)**

Best when SMEs provide corrected versions of poor outputs.

```python
result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="corrected"  # Use SME's corrected outputs
)
```

**Training data created:**
- Poor outputs → Use corrected version
- Good outputs → Use original
- Creates mix of corrections + positive examples

### **2. "positive" - Learn from Good Examples**

Best when you want to reinforce what works well.

```python
result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="positive",  # Only highly-rated outputs
    quality_threshold="good"  # Keep "good" and "excellent" only
)
```

**Training data created:**
- Only includes outputs rated "good" or better
- Reinforces successful patterns

### **3. "negative" - Learn from Corrections**

Best when focusing on fixing specific failure modes.

```python
result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="negative"  # Learn from poor outputs
)
```

**Training data created:**
- Only includes corrected versions of poor outputs
- Focuses on fixing problems

---

## 🔄 **Integration with MLflow Traces**

### **Option 1: Collect Feedback in MLflow UI**

SMEs can review traces in Databricks UI:

```python
# After running your agent, traces are logged
with mlflow.start_span("qa_interaction") as span:
    span.set_inputs({"question": question})
    output = my_agent(question)
    span.set_outputs({"answer": output})
    # Trace ID: span.trace_id

# SMEs review in UI and add feedback
# Then optimize directly from traces:

optimizer = HumanFeedbackOptimizer()

result = optimizer.optimize_from_traces(
    predict_fn=my_agent,
    experiment_id="my-exp-123",
    prompt_uris=["prompts:/qa/1"],
    feedback_name="quality",  # Name of SME feedback
    feedback_strategy="corrected"
)
```

### **Option 2: Programmatic Feedback with Corrections**

```python
from optimization.human_feedback_optimizer import log_corrected_feedback

# SME reviews production output
trace_id = "abc123"
original_output = "AI is computers"
sme_corrected = "AI (Artificial Intelligence) is..."

# Log correction
log_corrected_feedback(
    trace_id=trace_id,
    assessment_name="quality",
    assessment_value="poor",
    corrected_output=sme_corrected,
    rationale="Original too vague, needs detail",
    source_id="sme_john_doe"
)

# Later, optimize from all corrections
result = optimizer.optimize_from_traces(
    predict_fn=my_agent,
    experiment_id="my-exp-123",
    prompt_uris=["prompts:/qa/1"],
    feedback_name="quality"
)
```

---

## 📋 **Complete Workflow Example**

### **Phase 1: Deploy & Collect Feedback**

```python
import mlflow
from mlflow.entities import AssessmentSource, AssessmentSourceType

# Deploy your agent
mlflow.set_experiment("/Shared/customer_qa")

# Run agent on production queries
queries = [
    "What is your return policy?",
    "How do I track my order?",
    "What payment methods do you accept?"
]

trace_ids = []
for query in queries:
    with mlflow.start_span("customer_qa") as span:
        span.set_inputs({"query": query})

        # Your agent
        answer = customer_qa_agent(query)

        span.set_outputs({"answer": answer})
        trace_ids.append(span.trace_id)

print(f"Collected {len(trace_ids)} interactions")
```

### **Phase 2: SME Reviews & Corrects**

```python
from optimization.human_feedback_optimizer import log_corrected_feedback

# SME reviews and provides corrections
reviews = [
    {
        "trace_id": trace_ids[0],
        "assessment": "poor",
        "corrected": "Our return policy allows returns within 30 days with receipt...",
        "rationale": "Original answer was incomplete"
    },
    {
        "trace_id": trace_ids[1],
        "assessment": "excellent",
        # No correction needed!
    },
    {
        "trace_id": trace_ids[2],
        "assessment": "fair",
        "corrected": "We accept Visa, Mastercard, PayPal, and Apple Pay...",
        "rationale": "Missing Apple Pay option"
    }
]

# Log all SME feedback
for review in reviews:
    if "corrected" in review:
        log_corrected_feedback(
            trace_id=review["trace_id"],
            assessment_name="customer_satisfaction",
            assessment_value=review["assessment"],
            corrected_output=review["corrected"],
            rationale=review.get("rationale"),
            source_id="sme_team"
        )
    else:
        # Just log assessment (no correction)
        mlflow.log_feedback(
            trace_id=review["trace_id"],
            name="customer_satisfaction",
            value=review["assessment"],
            source=AssessmentSource(
                source_type=AssessmentSourceType.HUMAN,
                source_id="sme_team"
            )
        )
```

### **Phase 3: Optimize from Feedback**

```python
from optimization import HumanFeedbackOptimizer

optimizer = HumanFeedbackOptimizer()

# Optimize directly from SME feedback
result = optimizer.optimize_from_traces(
    predict_fn=lambda inputs: customer_qa_agent(inputs["query"]),
    experiment_id=mlflow.get_experiment_by_name("/Shared/customer_qa").experiment_id,
    prompt_uris=["prompts:/customer_qa/1"],
    feedback_name="customer_satisfaction",
    feedback_strategy="corrected",
    scorers=["correctness", "professionalism"]
)

print(f"✅ Optimized from {result.metadata['used_feedback']} SME corrections")
print(f"📈 Improvement: {result.improvement:.2%}")

# Deploy optimized prompt
optimized_prompt = result.optimized_prompts[0]
print(f"🚀 New prompt version: {optimized_prompt.uri}")
```

### **Phase 4: Validate & Deploy**

```python
# Test on held-out set
test_queries = ["What's your shipping time?", "Can I cancel my order?"]

for query in test_queries:
    old_answer = customer_qa_agent_v1(query)
    new_answer = customer_qa_agent_v2(query)  # Uses optimized prompt

    print(f"Q: {query}")
    print(f"Old: {old_answer}")
    print(f"New: {new_answer}")
    print()

# Deploy if better
# Update production agent to use optimized_prompt.uri
```

---

## 🆚 **Comparison: Judge Alignment vs Direct Feedback**

| Aspect | Judge Alignment | Direct Feedback (Ours) |
|--------|----------------|------------------------|
| **Steps** | 4 (create judge → align → generate → optimize) | 1 (optimize) |
| **Dependencies** | Requires LLM judges | No dependencies |
| **Flexibility** | Judge-specific format | Any feedback format |
| **Cost** | Judge calls + alignment + GEPA | Only GEPA |
| **SME Control** | Indirect (via judge) | Direct |
| **Use Case** | When judges are already deployed | When starting fresh |

**When to use Judge Alignment:**
- ✅ You already have deployed LLM judges
- ✅ Judges are working well, just need tuning
- ✅ Want systematic judge improvement

**When to use Direct Feedback (this module):**
- ✅ Starting prompt optimization from scratch
- ✅ Want direct SME control
- ✅ Don't want judge dependency
- ✅ Have clear ground truth or corrections

---

## 🎨 **Advanced: Custom Feedback Formats**

### **Example: Pairwise Comparisons**

```python
# SMEs prefer output A over output B
pairwise_feedback = [
    {
        "inputs": {"question": "What is AI?"},
        "outputs": {"answer_a": "AI is computers", "answer_b": "AI is intelligence"},
        "human_assessment": "prefer_b",
        "corrected_output": "AI is intelligence"  # Use preferred answer
    }
]

result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=pairwise_feedback,
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="corrected"
)
```

### **Example: Multi-dimensional Feedback**

```python
# SMEs rate multiple aspects
multidim_feedback = [
    {
        "inputs": {"question": "Explain quantum computing"},
        "outputs": {"answer": "..."},
        "human_assessment": "poor",
        "corrected_output": "...",
        "feedback_dimensions": {
            "accuracy": "good",
            "completeness": "poor",
            "clarity": "fair"
        }
    }
]

# Can filter by specific dimension
result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=[
        f for f in multidim_feedback
        if f["feedback_dimensions"]["accuracy"] == "poor"
    ],
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="corrected"
)
```

---

## 📚 **API Reference**

### **HumanFeedbackOptimizer**

```python
class HumanFeedbackOptimizer:
    def __init__(
        self,
        gepa_reflection_model: str = "databricks-claude-sonnet-4",
        gepa_max_calls: int = 100
    )

    def optimize_from_feedback(
        self,
        predict_fn: Callable,
        feedback: List[Dict[str, Any]],
        prompt_uris: List[str],
        feedback_strategy: str = "corrected",
        quality_threshold: Optional[str] = None,
        **kwargs
    ) -> GepaResult

    def optimize_from_traces(
        self,
        predict_fn: Callable,
        experiment_id: str,
        prompt_uris: List[str],
        feedback_name: str,
        feedback_strategy: str = "corrected",
        quality_threshold: Optional[str] = None,
        max_traces: int = 100,
        **kwargs
    ) -> GepaResult
```

### **Helper Functions**

```python
def log_corrected_feedback(
    trace_id: str,
    assessment_name: str,
    assessment_value: str,
    corrected_output: str,
    rationale: Optional[str] = None,
    source_id: str = "sme_correction"
)
```

---

## ✅ **Benefits for ANZ Customers**

### **For Customers Who:**

1. **Have SME teams reviewing outputs**
   - ✅ Direct feedback loop
   - ✅ No need to train on LLM judges
   - ✅ SME corrections become training data

2. **Want simple workflows**
   - ✅ One-step optimization
   - ✅ No complex judge alignment
   - ✅ Works with existing review processes

3. **Have domain experts**
   - ✅ Expert corrections directly improve prompts
   - ✅ No intermediate judge interpretation
   - ✅ Full control over quality standards

4. **Cost-conscious**
   - ✅ Skip judge creation and alignment costs
   - ✅ Only pay for GEPA optimization
   - ✅ Faster iteration cycles

---

## 🔄 **Migration Path**

### **If Already Using Judge Alignment:**

You can still benefit:

```python
# Extract ground truth from aligned judge
aligned_judge_output = aligned_judge(inputs=inputs, outputs=outputs)

# Use as training data for direct optimization
feedback = [{
    "inputs": inputs,
    "outputs": outputs,
    "human_assessment": "excellent",
    "corrected_output": aligned_judge_output.rationale  # Judge's assessment
}]

# Further optimize
result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/my_agent/1"]
)
```

---

## 📖 **See Also**

- **GEPA Optimization**: `docs/GEPA_OPTIMIZATION.md`
- **Judge Alignment** (Databricks): https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/align-judges
- **Optimizer Comparison**: `docs/OPTIMIZER_COMPARISON.md`

---

**This module eliminates the judge dependency and gives you direct control over prompt optimization from human feedback!** 🎯
