# Complete GEPA Guide: DSPy + MLflow

**The complete guide to using GEPA across both DSPy and MLflow ecosystems.**

---

## 🎯 **GEPA: Two Implementations, One Goal**

GEPA (Generative Edit-based Prompt Adaptation) exists in both DSPy and MLflow. This framework integrates **BOTH**!

| Implementation | Use For | Framework Required |
|----------------|---------|-------------------|
| **DSPy GEPA** | DSPy programs (ChainOfThought, ReAct) | DSPy |
| **MLflow GEPA** | Any agent (framework-agnostic) | MLflow |

---

## 📊 **Quick Decision Matrix**

| Your Situation | Use This |
|----------------|----------|
| Building with DSPy modules | **DSPy GEPA** |
| Have existing non-DSPy agent | **MLflow GEPA** |
| Want DSPy benefits + MLflow registry | **Both!** (DSPy → MLflow) |
| Have SME ratings (not corrections) | **MLflow GEPA + Custom Scorer** |

---

## 🚀 **Option 1: DSPy GEPA**

### **When to Use**

✅ You're using DSPy modules (ChainOfThought, ReAct, etc.)
✅ You want programmatic prompt control
✅ Math/reasoning/multi-step tasks
✅ You like DSPy's compositional approach
✅ **Production optimization** of DSPy programs via MLflow scorers
✅ **Automated pipelines** reading from production evals
✅ **Push to UC registry** for continuous improvement

### **Example: Math Solver**

```python
import dspy
from optimization import DSPyGepaOptimizer

# Configure DSPy
lm = dspy.LM("openai/gpt-4.1-mini", api_key="...")
dspy.configure(lm=lm)

# Define DSPy program
class MathSolver(dspy.Module):
    def __init__(self):
        self.solve = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.solve(question=question)

# Prepare training data
trainset = [
    dspy.Example(question="What is 2+2?", answer="4").with_inputs("question"),
    dspy.Example(question="What is 3*5?", answer="15").with_inputs("question"),
    # ... more examples
]

valset = [
    dspy.Example(question="What is 10-3?", answer="7").with_inputs("question"),
    # ... more validation examples
]

# Define metric
def accuracy(example, pred, trace=None):
    return 1.0 if example.answer.strip() == pred.answer.strip() else 0.0

# Optimize with DSPy GEPA
optimizer = DSPyGepaOptimizer(auto="light")  # light/medium/heavy

result = optimizer.optimize(
    program=MathSolver(),
    trainset=trainset,
    valset=valset,
    metric=accuracy
)

# Use optimized program
optimized_solver = result.optimized_program
answer = optimized_solver(question="What is 7+8?")
print(f"Answer: {answer.answer}")
```

### **Performance**

From [DSPy tutorial](https://dspy.ai/tutorials/gepa_aime/#optimize-the-program-with-dspygepa):
- **AIME 2025:** 46.6% → 56.6% (10% improvement)
- **Budget:** `auto="light"` (fast)

---

## 🔧 **Option 2: MLflow GEPA**

### **When to Use**

✅ You have any Python function (not DSPy)
✅ Framework-agnostic optimization
✅ Want MLflow Prompt Registry integration
✅ Have production usage data

### **Example: Custom Agent**

```python
import mlflow
from mlflow.deployments import get_deploy_client
from optimization import GepaOptimizer

# Your existing agent (ANY framework!)
def customer_support_agent(query: str) -> str:
    prompt = mlflow.genai.load_prompt("prompts:/support/1")

    client = get_deploy_client("databricks")
    response = client.predict(
        endpoint="databricks-claude-sonnet-4",
        inputs={
            "messages": [{
                "role": "user",
                "content": prompt.format(query=query)
            }]
        }
    )

    return response["choices"][0]["message"]["content"]

# Register initial prompt
prompt = mlflow.genai.register_prompt(
    name="customer_support",
    template="Answer the customer query professionally: {{query}}"
)

# Training data from production logs
train_data = [
    {
        "inputs": {"query": "How do I return an item?"},
        "expectations": {"expected_response": "You can return items within..."}
    },
    {
        "inputs": {"query": "What's your refund policy?"},
        "expectations": {"expected_response": "We offer full refunds..."}
    },
    # ... more examples
]

# Optimize with MLflow GEPA
optimizer = GepaOptimizer(
    reflection_model="databricks-claude-sonnet-4",
    max_metric_calls=100
)

result = optimizer.optimize(
    predict_fn=lambda inputs: customer_support_agent(inputs["query"]),
    train_data=train_data,
    prompt_uris=[prompt.uri],
    scorers=["correctness", "professionalism"]
)

# Use optimized prompt
optimized_prompt = result.optimized_prompts[0]
print(f"Optimized prompt URI: {optimized_prompt.uri}")
```

---

## 🏭 **Production Optimization with DSPy GEPA**

### **Automated Production Pipeline**

DSPy GEPA can read from MLflow scorers/evals and push optimized prompts to UC registry for **fully automated production optimization**.

```python
import dspy
import mlflow
from mlflow.genai.scorers import Correctness, Relevance
from optimization import DSPyGepaOptimizer

# Configure DSPy with Databricks
lm = dspy.LM("databricks/databricks-claude-sonnet-4")
dspy.configure(lm=lm)

# Your production DSPy agent
class ProductionAgent(dspy.Module):
    def __init__(self):
        self.answer = dspy.ChainOfThought("query -> response")

    def forward(self, query):
        return self.answer(query=query)

# Load production data from MLflow
def load_production_data_from_mlflow(experiment_id: str):
    """Load eval data from MLflow experiments"""
    runs = mlflow.search_runs(experiment_ids=[experiment_id])

    examples = []
    for _, run in runs.iterrows():
        # Extract inputs and ground truth from MLflow traces
        inputs = run["params.input"]
        expected = run["params.expected_output"]

        examples.append(
            dspy.Example(query=inputs, response=expected).with_inputs("query")
        )

    return examples

# Define metric using MLflow scorers
def create_mlflow_based_metric(scorers: list):
    """Convert MLflow scorers to DSPy metric"""
    def metric(example, pred, trace=None):
        scores = []
        for scorer in scorers:
            score = scorer(
                outputs=pred.response,
                expectations={"expected_response": example.response}
            )
            scores.append(score)
        return sum(scores) / len(scores)  # Average
    return metric

# Load production feedback
trainset = load_production_data_from_mlflow(experiment_id="prod-agent-123")
valset = load_production_data_from_mlflow(experiment_id="prod-agent-val")

# Define MLflow-based metric
mlflow_scorers = [
    Correctness(model="databricks-claude-sonnet-4"),
    Relevance(model="databricks-claude-sonnet-4")
]
metric = create_mlflow_based_metric(mlflow_scorers)

# Optimize with DSPy GEPA
optimizer = DSPyGepaOptimizer(auto="medium")

result = optimizer.optimize(
    program=ProductionAgent(),
    trainset=trainset,
    valset=valset,
    metric=metric
)

print(f"✅ Optimization complete!")
print(f"   Initial Score: {result.initial_score:.2f}")
print(f"   Final Score: {result.final_score:.2f}")
print(f"   Improvement: {result.improvement*100:.1f}%")

# Extract optimized prompts
optimized_prompts = optimizer.extract_prompts(result.optimized_program)

# Push to UC Prompt Registry
for module_name, prompt_template in optimized_prompts.items():
    prompt = mlflow.genai.register_prompt(
        name=f"production_agent_{module_name}",
        template=prompt_template,
        tags={
            "optimizer": "dspy_gepa",
            "initial_score": str(result.initial_score),
            "final_score": str(result.final_score),
            "improvement": f"{result.improvement*100:.1f}%",
            "experiment_id": "prod-agent-123"
        }
    )
    print(f"📦 Registered to UC: {prompt.uri}")

# Deploy optimized agent
optimized_agent = result.optimized_program

# Use in production
response = optimized_agent(query="How do I reset my password?")
print(f"🤖 Response: {response.response}")
```

### **Continuous Improvement Pipeline**

Set up an automated pipeline for continuous optimization:

```python
import schedule
import time

def continuous_optimization_pipeline():
    """Run daily optimization based on production data"""

    # 1. Load yesterday's production data
    trainset = load_production_data_from_mlflow(
        experiment_id="prod-agent-123",
        date_range="yesterday"
    )

    # 2. Optimize if we have enough new data
    if len(trainset) >= 50:
        optimizer = DSPyGepaOptimizer(auto="light")  # Fast optimization

        result = optimizer.optimize(
            program=ProductionAgent(),
            trainset=trainset,
            metric=mlflow_based_metric
        )

        # 3. Only deploy if improvement is significant
        if result.improvement > 0.05:  # >5% improvement
            # Extract and register
            prompts = optimizer.extract_prompts(result.optimized_program)
            for name, template in prompts.items():
                mlflow.genai.register_prompt(
                    name=f"production_agent_{name}",
                    template=template
                )

            print(f"✅ Deployed new version with {result.improvement*100:.1f}% improvement")
        else:
            print(f"⏭️  Skipped deployment (improvement: {result.improvement*100:.1f}%)")
    else:
        print(f"⏭️  Insufficient data ({len(trainset)} examples, need 50)")

# Schedule daily optimization
schedule.every().day.at("03:00").do(continuous_optimization_pipeline)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

### **A/B Testing with Multiple Versions**

```python
def ab_test_optimized_prompts():
    """Compare production agent with optimized version"""

    # Load both versions
    baseline_prompt = mlflow.genai.load_prompt("prompts:/production_agent/1")
    optimized_prompt = mlflow.genai.load_prompt("prompts:/production_agent/2")

    # Test set
    test_queries = load_production_data_from_mlflow(experiment_id="test-set")

    # Evaluate both
    baseline_scores = []
    optimized_scores = []

    for example in test_queries:
        # Baseline
        baseline_response = baseline_agent(example.query)
        baseline_score = metric(example, baseline_response)
        baseline_scores.append(baseline_score)

        # Optimized
        optimized_response = optimized_agent(example.query)
        optimized_score = metric(example, optimized_response)
        optimized_scores.append(optimized_score)

    # Compare
    avg_baseline = sum(baseline_scores) / len(baseline_scores)
    avg_optimized = sum(optimized_scores) / len(optimized_scores)

    print(f"📊 A/B Test Results:")
    print(f"   Baseline (v1):  {avg_baseline:.2f}")
    print(f"   Optimized (v2): {avg_optimized:.2f}")
    print(f"   Improvement:    {(avg_optimized - avg_baseline) / avg_baseline * 100:.1f}%")

    # Auto-promote if better
    if avg_optimized > avg_baseline:
        mlflow.genai.set_production_version("production_agent", version=2)
        print(f"✅ Promoted v2 to production")
```

---

## 🔄 **Option 3: Best of Both Worlds**

### **Workflow: DSPy GEPA → MLflow Registry**

Use DSPy GEPA for optimization, then save to MLflow for production.

```python
import dspy
import mlflow
from optimization import DSPyGepaOptimizer

# 1. Optimize with DSPy GEPA
dspy_optimizer = DSPyGepaOptimizer(auto="medium")

result = dspy_optimizer.optimize(
    program=MyDSPyProgram(),
    trainset=trainset,
    valset=valset,
    metric=accuracy
)

# 2. Extract optimized prompts
prompts = dspy_optimizer.extract_prompts(result.optimized_program)

# 3. Register in MLflow for production
for module_name, prompt_text in prompts.items():
    mlflow_prompt = mlflow.genai.register_prompt(
        name=f"dspy_{module_name}_optimized",
        template=prompt_text,
        tags={"optimizer": "dspy_gepa", "score": str(result.optimized_score)}
    )
    print(f"Registered: {mlflow_prompt.uri}")

# 4. Use in production (non-DSPy code)
def production_agent(question: str):
    # Load DSPy-optimized prompt from MLflow
    prompt = mlflow.genai.load_prompt("prompts:/dspy_solve_optimized/1")
    return llm.call(prompt)
```

---

## 💡 **Option 4: SME Ratings as Metrics**

### **When SMEs Only Rate (Don't Correct)**

```python
from optimization import HumanFeedbackOptimizer

# SME feedback with ratings only
feedback = [
    {
        "inputs": {"query": "How do I track my order?"},
        "sme_rating": "excellent"
    },
    {
        "inputs": {"query": "What's your return policy?"},
        "sme_rating": "poor"  # No correction provided!
    },
    {
        "inputs": {"query": "Do you ship internationally?"},
        "sme_rating": "fair"
    },
]

# Optimize using ratings as metric
optimizer = HumanFeedbackOptimizer()

result = optimizer.optimize_from_feedback(
    predict_fn=my_agent,
    feedback=feedback,
    prompt_uris=["prompts:/agent/1"],
    use_ratings_as_metric=True  # Use ratings directly
)

print(f"Optimized from {len(feedback)} SME ratings")
```

---

## 📈 **Performance Comparison**

### **DSPy GEPA Results**

From [DSPy tutorial](https://dspy.ai/tutorials/gepa_aime/#optimize-the-program-with-dspygepa):
- **AIME Math:** 46.6% → 56.6% (+10%)
- **Budget:** `auto="light"` (~50 metric calls)

### **MLflow GEPA Results**

From Databricks blog:
- **IE Bench:** Open-source surpassed Claude Opus 4.1 by ~3%
- **Cost:** 90x cheaper with similar quality
- **Frontier models:** +6-7% improvement

---

## 🛠️ **Unified API: PromptOptimizer**

Use one class for all optimization methods:

```python
from optimization import PromptOptimizer

optimizer = PromptOptimizer()

# DSPy GEPA
result1 = optimizer.optimize_with_dspy_gepa(
    program=dspy_program,
    trainset=trainset,
    metric=accuracy
)

# MLflow GEPA
result2 = optimizer.optimize_with_gepa(
    predict_fn=any_function,
    train_data=train_data,
    prompt_uris=["prompts:/agent/1"]
)

# SME Ratings
result3 = optimizer.optimize_from_feedback(
    predict_fn=any_function,
    feedback=sme_feedback,
    prompt_uris=["prompts:/agent/1"],
    use_ratings_as_metric=True
)
```

---

## 🎨 **Advanced: Convert Between Formats**

### **Standard Data → DSPy Examples**

```python
from optimization.dspy_gepa_optimizer import convert_to_dspy_examples

# Standard format
data = [
    {"question": "2+2?", "answer": "4"},
    {"question": "3+3?", "answer": "6"}
]

# Convert to DSPy format
dspy_examples = convert_to_dspy_examples(
    data=data,
    input_keys=["question"],
    output_key="answer"
)

# Use with DSPy GEPA
result = optimizer.optimize_with_dspy_gepa(
    program=program,
    trainset=dspy_examples,
    metric=accuracy
)
```

### **Custom Scoring → DSPy Metric**

```python
from optimization.dspy_gepa_optimizer import create_dspy_metric

# Simple scoring function
def my_accuracy(expected, predicted):
    return 1.0 if expected == predicted else 0.0

# Convert to DSPy metric
dspy_metric = create_dspy_metric(my_accuracy, name="accuracy")

# Use with DSPy GEPA
result = optimizer.optimize_with_dspy_gepa(
    program=program,
    trainset=trainset,
    metric=dspy_metric
)
```

---

## 🔄 **Complete Workflow Example**

### **Phase 1: Prototype with DSPy GEPA**

```python
import dspy
from optimization import DSPyGepaOptimizer

# Quick DSPy prototype
class CustomerSupport(dspy.Module):
    def __init__(self):
        self.answer = dspy.ChainOfThought("query -> response")

    def forward(self, query):
        return self.answer(query=query)

# Optimize quickly
optimizer = DSPyGepaOptimizer(auto="light")
result = optimizer.optimize(
    program=CustomerSupport(),
    trainset=initial_data,
    metric=quality_metric
)

# Extract prompt
prompts = optimizer.extract_prompts(result.optimized_program)
```

### **Phase 2: Deploy with MLflow**

```python
import mlflow

# Register DSPy-optimized prompt
prompt = mlflow.genai.register_prompt(
    name="customer_support_v1",
    template=prompts["answer"]
)

# Deploy agent using MLflow prompt
def production_agent(query):
    prompt = mlflow.genai.load_prompt("prompts:/customer_support_v1/1")
    return llm.call(prompt.format(query=query))
```

### **Phase 3: Continuous Improvement with MLflow GEPA**

```python
from optimization import GepaOptimizer

# Collect production feedback
production_feedback = collect_from_mlflow_traces(
    experiment_id="prod-support"
)

# Further optimize with MLflow GEPA
optimizer = GepaOptimizer()
result = optimizer.optimize(
    predict_fn=production_agent,
    train_data=production_feedback,
    prompt_uris=["prompts:/customer_support_v1/1"]
)

# New version automatically registered
v2_prompt = result.optimized_prompts[0]
```

---

## 📊 **Comparison Table**

| Feature | DSPy GEPA | MLflow GEPA |
|---------|-----------|-------------|
| **Input** | DSPy Module | Any function |
| **Output** | Optimized Module | Optimized prompts (MLflow) |
| **Framework** | DSPy-specific | Framework-agnostic |
| **Data Format** | dspy.Example | Dict with inputs/expectations |
| **Integration** | DSPy ecosystem | MLflow ecosystem |
| **Production** | ✅ Via MLflow scorers + UC registry | ✅ Native MLflow registry |
| **Automated Pipelines** | ✅ Read from MLflow evals | ✅ Read from production logs |
| **Flexibility** | Programmatic control | Works with any code |
| **Best For** | DSPy-based agents (dev + prod) | Non-DSPy agents |

---

## ✅ **Recommendations**

### **For DSPy-Based Agents:**

1. **Use DSPy GEPA** for optimization (development + production)
2. **Integrate with MLflow** for scoring and evaluation
3. **Push to UC registry** for continuous deployment
4. **Automate optimization** pipelines with production data

### **For Non-DSPy Agents:**

1. **Use MLflow GEPA directly** (no rewrite needed)
2. **Collect SME feedback** as ratings or corrections
3. **Optimize continuously** from production logs
4. **Framework-agnostic** - works with any Python function

### **For ANZ Customers:**

1. **MLflow GEPA** for framework-agnostic optimization
2. **SME ratings as metrics** for fast feedback cycles
3. **No judge dependency** required

---

## 📚 **API Reference**

### **DSPy GEPA**

```python
from optimization import DSPyGepaOptimizer

optimizer = DSPyGepaOptimizer(
    auto: str = "medium",  # light/medium/heavy
    max_bootstrapped_demos: int = 4,
    max_labeled_demos: int = 8,
    max_rounds: int = 3
)

result = optimizer.optimize(
    program: dspy.Module,
    trainset: List[dspy.Example],
    valset: Optional[List] = None,
    metric: Optional[Callable] = None
)
```

### **MLflow GEPA**

```python
from optimization import GepaOptimizer

optimizer = GepaOptimizer(
    reflection_model: str = "databricks-claude-sonnet-4",
    max_metric_calls: int = 100
)

result = optimizer.optimize(
    predict_fn: Callable,
    train_data: List[Dict],
    prompt_uris: List[str],
    scorers: Optional[List] = None
)
```

---

## 🔗 **References**

- **DSPy GEPA Tutorial**: https://dspy.ai/tutorials/gepa_aime/
- **MLflow GEPA Docs**: https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/
- **Databricks Blog**: https://www.databricks.com/blog/building-state-art-enterprise-agents-90x-cheaper-automated-prompt-optimization

---

**You now have complete GEPA coverage: DSPy, MLflow, and SME feedback - all integrated!** 🎉
