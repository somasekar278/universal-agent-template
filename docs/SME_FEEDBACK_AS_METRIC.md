# SME Feedback as Direct GEPA Metric

**Use SME ratings directly as optimization metrics - no corrections needed!**

Based on the insight that GEPA (both [DSPy](https://dspy.ai/tutorials/gepa_aime/#optimize-the-program-with-dspygepa) and MLflow) accepts custom metrics.

---

## 🎯 **Two Approaches to SME Feedback**

### **Approach 1: Feedback → Training Data**

SME provides **corrected outputs** → Used as ground truth

```python
feedback = [{
    "inputs": {"question": "What is AI?"},
    "outputs": {"answer": "AI is computers"},
    "corrected_output": "AI is artificial intelligence..."  # Full correction
}]

result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/qa/1"],
    feedback_strategy="corrected"  # Use corrections as expected outputs
)
```

**Best when:** SMEs can provide full corrected outputs

---

### **Approach 2: Feedback → Custom Metric** ⭐ **NEW**

SME provides **ratings only** → Used as optimization metric

```python
feedback = [{
    "inputs": {"question": "What is AI?"},
    "sme_rating": "poor"  # Just the rating!
}, {
    "inputs": {"question": "What is ML?"},
    "sme_rating": "excellent"  # No correction needed
}]

result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/qa/1"],
    use_ratings_as_metric=True  # Use ratings as metric
)
```

**Best when:** SMEs only rate (don't provide corrections)

---

## 🚀 **Quick Comparison**

| Aspect | Training Data Approach | Metric Approach |
|--------|----------------------|-----------------|
| **SME provides** | Corrected outputs | Ratings only |
| **SME effort** | High (write corrections) | Low (just rate) |
| **Optimization** | Learn from corrections | Maximize ratings |
| **Best for** | Clear errors | Subjective quality |
| **Example** | "Wrong answer" → correct it | "Not professional enough" → rate it |

---

## 📊 **Complete Example: Both Approaches**

### **Scenario: Customer Support Agent**

```python
from optimization import HumanFeedbackOptimizer
import mlflow

# Your agent
def support_agent(query: str) -> str:
    prompt = mlflow.genai.load_prompt("prompts:/support/1")
    return llm.call(prompt.format(query=query))

# Production interactions
interactions = [
    {
        "query": "How do I return an item?",
        "agent_response": "You can return items."
    },
    {
        "query": "What's your refund policy?",
        "agent_response": "We offer refunds within 30 days with receipt and original packaging."
    },
    {
        "query": "Do you ship internationally?",
        "agent_response": "Yes we ship everywhere."
    }
]
```

### **Approach 1: SME Provides Corrections**

```python
# SME reviews and corrects poor responses
feedback_with_corrections = [
    {
        "inputs": {"query": "How do I return an item?"},
        "outputs": {"response": "You can return items."},
        "sme_rating": "poor",
        "corrected_output": "You can return items within 30 days by following these steps: 1) Contact support..."
    },
    {
        "inputs": {"query": "What's your refund policy?"},
        "outputs": {"response": "We offer refunds within 30 days..."},
        "sme_rating": "excellent"  # No correction needed
    },
    {
        "inputs": {"query": "Do you ship internationally?"},
        "outputs": {"response": "Yes we ship everywhere."},
        "sme_rating": "fair",
        "corrected_output": "Yes, we ship to over 50 countries. Shipping costs vary by destination..."
    }
]

# Optimize from corrections
optimizer = HumanFeedbackOptimizer()

result = optimizer.optimize_from_feedback(
    predict_fn=lambda inputs: support_agent(inputs["query"]),
    feedback=feedback_with_corrections,
    prompt_uris=["prompts:/support/1"],
    feedback_strategy="corrected"  # Use SME corrections
)

print(f"Improvement: {result.improvement:.2%}")
```

### **Approach 2: SME Only Rates**

```python
# SME just rates (much faster!)
feedback_with_ratings = [
    {
        "inputs": {"query": "How do I return an item?"},
        "sme_rating": "poor"
    },
    {
        "inputs": {"query": "What's your refund policy?"},
        "sme_rating": "excellent"
    },
    {
        "inputs": {"query": "Do you ship internationally?"},
        "sme_rating": "fair"
    },
    # 50 more ratings...
]

# Optimize to maximize ratings
result = optimizer.optimize_from_feedback(
    predict_fn=lambda inputs: support_agent(inputs["query"]),
    feedback=feedback_with_ratings,
    prompt_uris=["prompts:/support/1"],
    use_ratings_as_metric=True  # Use ratings as metric!
)

print(f"Improvement: {result.improvement:.2%}")
```

---

## 🎨 **Custom Rating Schemes**

### **Example 1: Binary Approval**

```python
from optimization import create_sme_feedback_scorer

# Custom rating scheme
custom_scorer = create_sme_feedback_scorer({
    "approved": 1.0,
    "rejected": 0.0
})

feedback = [
    {"inputs": {...}, "sme_rating": "approved"},
    {"inputs": {...}, "sme_rating": "rejected"},
]

result = optimizer.optimize_with_sme_ratings(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/agent/1"],
    rating_map={"approved": 1.0, "rejected": 0.0}
)
```

### **Example 2: Star Ratings**

```python
# 5-star rating system
star_scorer = create_sme_feedback_scorer({
    "5_stars": 1.0,
    "4_stars": 0.75,
    "3_stars": 0.5,
    "2_stars": 0.25,
    "1_star": 0.0
})

feedback = [
    {"inputs": {...}, "sme_rating": "3_stars"},
    {"inputs": {...}, "sme_rating": "5_stars"},
]

result = optimizer.optimize_with_sme_ratings(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/agent/1"],
    rating_map={
        "5_stars": 1.0,
        "4_stars": 0.75,
        "3_stars": 0.5,
        "2_stars": 0.25,
        "1_star": 0.0
    }
)
```

### **Example 3: Multi-Dimensional Ratings**

```python
# Rate multiple aspects
feedback = [
    {
        "inputs": {"query": "..."},
        "accuracy_rating": "good",
        "tone_rating": "excellent",
        "completeness_rating": "fair"
    }
]

# Create scorer for each dimension
accuracy_scorer = create_sme_feedback_scorer()  # Default mapping

def combined_scorer(outputs, expectations):
    """Combine multiple rating dimensions."""
    accuracy = accuracy_scorer(outputs, {"sme_rating": expectations["accuracy_rating"]})
    tone = accuracy_scorer(outputs, {"sme_rating": expectations["tone_rating"]})
    completeness = accuracy_scorer(outputs, {"sme_rating": expectations["completeness_rating"]})

    # Weighted average
    return 0.5 * accuracy + 0.3 * tone + 0.2 * completeness

# Use custom combined scorer
result = optimizer.optimize(
    predict_fn=my_agent,
    train_data=[{
        "inputs": f["inputs"],
        "expectations": {
            "accuracy_rating": f["accuracy_rating"],
            "tone_rating": f["tone_rating"],
            "completeness_rating": f["completeness_rating"]
        }
    } for f in feedback],
    prompt_uris=["prompts:/agent/1"],
    scorers=[combined_scorer]
)
```

---

## 🔄 **Integration with MLflow Traces**

### **Log Ratings to Traces**

```python
import mlflow
from mlflow.entities import AssessmentSource, AssessmentSourceType

# After agent runs
with mlflow.start_span("support_query") as span:
    span.set_inputs({"query": query})
    response = support_agent(query)
    span.set_outputs({"response": response})

    # SME reviews and rates (no correction needed)
    mlflow.log_feedback(
        trace_id=span.trace_id,
        name="sme_quality",
        value="fair",  # Just the rating
        source=AssessmentSource(
            source_type=AssessmentSourceType.HUMAN,
            source_id="sme_alice"
        )
    )
```

### **Optimize from Traced Ratings**

```python
# Later, optimize from all ratings
result = optimizer.optimize_from_traces(
    predict_fn=support_agent,
    experiment_id="support-exp-123",
    prompt_uris=["prompts:/support/1"],
    feedback_name="sme_quality",
    use_ratings_as_metric=True  # Use ratings directly!
)
```

---

## 🆚 **When to Use Each Approach**

### **Use Training Data Approach (Corrections) When:**

✅ SMEs can provide full corrected outputs
✅ There are clear right/wrong answers
✅ You have factual/technical content
✅ Errors are objective

**Examples:**
- Technical documentation
- Code generation
- Data extraction
- Math/logic problems

### **Use Metric Approach (Ratings) When:**

✅ SMEs can only rate (not correct)
✅ Quality is subjective
✅ You need faster SME review cycles
✅ Tone/style matters more than facts

**Examples:**
- Customer support tone
- Marketing copy
- Creative writing
- Subjective quality assessment

### **Use Both When:**

✅ Mix of objective and subjective quality
✅ Some outputs need correction, others just rating
✅ You want maximum signal from SME feedback

**Example:**
```python
# Some feedback has corrections
corrections_feedback = [
    {"inputs": {...}, "corrected_output": "..."}
]

# Some feedback just has ratings
ratings_feedback = [
    {"inputs": {...}, "sme_rating": "excellent"}
]

# Optimize from corrections first
result1 = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=corrections_feedback,
    prompt_uris=["prompts:/agent/1"],
    feedback_strategy="corrected"
)

# Then further optimize from ratings
result2 = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=ratings_feedback,
    prompt_uris=[result1.optimized_prompts[0].uri],  # Start from optimized
    use_ratings_as_metric=True
)
```

---

## 📚 **API Reference**

### **Rating-Based Optimization**

```python
# Create custom scorer
scorer = create_sme_feedback_scorer(
    rating_map: Optional[Dict[str, float]] = None
)

# Optimize with ratings
result = optimizer.optimize_from_feedback(
    predict_fn: Callable,
    feedback: List[Dict],
    prompt_uris: List[str],
    use_ratings_as_metric: bool = True,  # KEY: Use ratings as metric
    rating_map: Optional[Dict[str, float]] = None
)

# Or directly
result = optimizer.optimize_with_sme_ratings(
    predict_fn: Callable,
    feedback: List[Dict],
    prompt_uris: List[str],
    rating_map: Optional[Dict[str, float]] = None
)
```

---

## ✅ **Benefits for ANZ Customers**

### **Faster SME Review Cycles**
- ✅ SME just clicks a rating (5 seconds)
- ❌ vs writing full correction (2-5 minutes)
- **Result:** 60x faster feedback collection!

### **More Feedback at Same Cost**
- ✅ Can review 100 outputs in time it took to correct 10
- ✅ More data = better optimization

### **Natural for Subjective Quality**
- ✅ "This feels unprofessional" → Rate "poor"
- ❌ vs trying to write "professional" version

### **Flexible Rating Schemes**
- ✅ Map to your existing review process
- ✅ Binary, stars, custom scales

---

## 📖 **See Also**

- **Human Feedback Optimization**: `docs/HUMAN_FEEDBACK_OPTIMIZATION.md`
- **GEPA Optimization**: `docs/GEPA_OPTIMIZATION.md`
- **DSPy GEPA**: https://dspy.ai/tutorials/gepa_aime/#optimize-the-program-with-dspygepa
- **MLflow Scorers**: https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/

---

**Now you have BOTH options: corrections OR ratings! Choose what works best for your SMEs.** 🎯
