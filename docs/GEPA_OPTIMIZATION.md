# GEPA Prompt Optimization

**Continuously improve your agent prompts using MLflow's GEPA optimizer.**

GEPA (Generative Edit-based Prompt Adaptation) uses LLM-driven reflection and automated feedback to iteratively refine prompts, leading to systematic improvements.

Based on: https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/

---

## 🎯 **When to Use GEPA**

| Scenario | Best Optimizer |
|----------|----------------|
| **Production optimization** | ✅ GEPA |
| **Have real usage data** | ✅ GEPA |
| **Multi-prompt workflows** | ✅ GEPA |
| **Model migration** | ✅ GEPA |
| **Initial prototyping** | DSPy |
| **System prompt tuning** | TextGrad |

---

## 🚀 **Quick Start**

### **Step 1: Register Your Prompt**

```python
import mlflow

prompt = mlflow.genai.register_prompt(
    name="qa_assistant",
    template="Answer the question: {{question}}"
)

print(f"Prompt URI: {prompt.uri}")  # prompts:/qa_assistant/1
```

### **Step 2: Define Your Agent Function**

```python
def my_agent(question: str) -> str:
    """Agent that uses the registered prompt."""
    prompt = mlflow.genai.load_prompt("prompts:/qa_assistant/1")

    # Call your LLM
    from mlflow.deployments import get_deploy_client
    client = get_deploy_client("databricks")

    response = client.predict(
        endpoint="databricks-claude-sonnet-4",
        inputs={
            "messages": [
                {"role": "user", "content": prompt.format(question=question)}
            ]
        }
    )

    return response["choices"][0]["message"]["content"]
```

### **Step 3: Prepare Training Data**

```python
train_data = [
    {
        "inputs": {"question": "What is 2+2?"},
        "expectations": {"expected_response": "4"}
    },
    {
        "inputs": {"question": "Capital of France?"},
        "expectations": {"expected_response": "Paris"}
    },
    # ... more examples
]
```

### **Step 4: Optimize**

```python
from optimization.prompt_optimizer import PromptOptimizer

optimizer = PromptOptimizer(
    gepa_reflection_model="databricks-claude-sonnet-4",
    gepa_max_calls=100
)

result = optimizer.optimize_with_gepa(
    predict_fn=my_agent,
    train_data=train_data,
    prompt_uris=["prompts:/qa_assistant/1"],
    scorers=["correctness"]
)

# Access optimized prompt
optimized = result.optimized_prompts[0]
print(f"Optimized template: {optimized.template}")
print(f"Improvement: {result.improvement:.2%}")
```

---

## 📊 **Complete Example: Optimizing L1 Chatbot**

```python
import mlflow
from mlflow.deployments import get_deploy_client
from optimization.prompt_optimizer import PromptOptimizer

# 1. Register L1's system prompt
prompt = mlflow.genai.register_prompt(
    name="l1_system_prompt",
    template="You are a helpful AI assistant. {{instruction}}"
)

# 2. Define L1 agent function
def l1_agent(user_message: str, instruction: str = "") -> str:
    """L1 chatbot that uses registered prompt."""
    prompt = mlflow.genai.load_prompt("prompts:/l1_system_prompt/1")

    llm_client = get_deploy_client("databricks")
    response = llm_client.predict(
        endpoint="databricks-claude-sonnet-4",
        inputs={
            "messages": [
                {"role": "system", "content": prompt.format(instruction=instruction)},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
    )

    return response["choices"][0]["message"]["content"]

# 3. Prepare training data from your logs
train_data = [
    {
        "inputs": {
            "user_message": "What's the weather?",
            "instruction": "Be concise"
        },
        "expectations": {
            "expected_response": "I cannot check real-time weather. Please check a weather service."
        }
    },
    {
        "inputs": {
            "user_message": "Tell me a joke",
            "instruction": "Be funny"
        },
        "expectations": {
            "expected_response": "Why don't scientists trust atoms? Because they make up everything!"
        }
    },
    # Add more examples from your actual usage logs
]

# 4. Optimize with GEPA
optimizer = PromptOptimizer()

result = optimizer.optimize_with_gepa(
    predict_fn=lambda inputs: l1_agent(
        user_message=inputs["user_message"],
        instruction=inputs["instruction"]
    ),
    train_data=train_data,
    prompt_uris=["prompts:/l1_system_prompt/1"],
    scorers=["correctness", "professionalism"]
)

# 5. Deploy optimized prompt
optimized_prompt = result.optimized_prompts[0]
print(f"✅ Optimized prompt registered: {optimized_prompt.uri}")
print(f"📈 Improvement: {result.improvement:.2%}")

# Update your L1 agent to use the optimized version
# Just change: mlflow.genai.load_prompt("prompts:/l1_system_prompt/2")
```

---

## 🔧 **Advanced: Multi-Prompt Optimization**

Optimize multiple prompts together (e.g., for L2 with planning + answering):

```python
# Register multiple prompts
plan_prompt = mlflow.genai.register_prompt(
    name="planner",
    template="Make a plan to answer: {{question}}"
)

answer_prompt = mlflow.genai.register_prompt(
    name="answerer",
    template="Answer {{question}} using plan: {{plan}}"
)

# Define multi-prompt agent
def l2_agent_with_planning(question: str) -> str:
    # Load prompts
    plan_prompt = mlflow.genai.load_prompt("prompts:/planner/1")
    answer_prompt = mlflow.genai.load_prompt("prompts:/answerer/1")

    client = get_deploy_client("databricks")

    # Step 1: Plan
    plan_response = client.predict(
        endpoint="databricks-claude-sonnet-4",
        inputs={
            "messages": [{"role": "user", "content": plan_prompt.format(question=question)}]
        }
    )
    plan = plan_response["choices"][0]["message"]["content"]

    # Step 2: Answer
    answer_response = client.predict(
        endpoint="databricks-claude-sonnet-4",
        inputs={
            "messages": [{
                "role": "user",
                "content": answer_prompt.format(question=question, plan=plan)
            }]
        }
    )

    return answer_response["choices"][0]["message"]["content"]

# Optimize both prompts together
result = optimizer.optimize_with_gepa(
    predict_fn=l2_agent_with_planning,
    train_data=train_data,
    prompt_uris=[
        "prompts:/planner/1",
        "prompts:/answerer/1"
    ],
    scorers=["correctness"]
)

# Access both optimized prompts
optimized_planner = result.optimized_prompts[0]
optimized_answerer = result.optimized_prompts[1]
```

---

## 🎨 **Custom Scorers**

Define custom evaluation metrics:

```python
from mlflow.genai.scorers import scorer

@scorer
def brevity_scorer(outputs: str):
    """Prefer shorter outputs (max 100 chars)."""
    return min(1.0, 100 / max(len(outputs), 1))

@scorer
def keyword_scorer(outputs: str, expectations: dict):
    """Check if output contains required keywords."""
    keywords = expectations.get("required_keywords", [])
    found = sum(1 for kw in keywords if kw.lower() in outputs.lower())
    return found / len(keywords) if keywords else 1.0

# Use custom scorers
result = optimizer.optimize_with_gepa(
    predict_fn=my_agent,
    train_data=train_data,
    prompt_uris=["prompts:/my_prompt/1"],
    scorers=[brevity_scorer, keyword_scorer, "correctness"]
)
```

---

## 📈 **Model Migration with GEPA**

When switching models (e.g., GPT-5 → GPT-5-mini for cost savings):

```python
# Original prompt optimized for GPT-5
original_prompt = mlflow.genai.load_prompt("prompts:/qa/1")

# Collect outputs from GPT-5 as expectations
train_data = []
for question in evaluation_questions:
    gpt5_output = call_gpt5(original_prompt.format(question=question))
    train_data.append({
        "inputs": {"question": question},
        "expectations": {"expected_response": gpt5_output}
    })

# Optimize for GPT-5-mini
def gpt5_mini_agent(question: str) -> str:
    prompt = mlflow.genai.load_prompt("prompts:/qa/1")
    return call_gpt5_mini(prompt.format(question=question))

result = optimizer.optimize_with_gepa(
    predict_fn=gpt5_mini_agent,
    train_data=train_data,
    prompt_uris=["prompts:/qa/1"],
    scorers=["correctness"]
)

# Now GPT-5-mini with optimized prompt matches GPT-5 quality!
```

---

## 🔄 **Integration with Evaluation Harness**

```python
from evaluation.harness import EvaluationHarness

# Run evaluation to get baseline
harness = EvaluationHarness()
baseline_results = harness.run_evaluation(
    agent=my_agent,
    test_data=test_data
)

# Convert eval results to training data
train_data = [
    {
        "inputs": result["inputs"],
        "expectations": {"expected_response": result["expected_output"]}
    }
    for result in baseline_results
]

# Optimize with GEPA
optimizer = PromptOptimizer()
result = optimizer.optimize_with_gepa(
    predict_fn=my_agent,
    train_data=train_data,
    prompt_uris=["prompts:/my_agent/1"],
    scorers=["correctness"]
)

# Re-run evaluation with optimized prompt
optimized_results = harness.run_evaluation(
    agent=my_agent,  # Now uses optimized prompt
    test_data=test_data
)

print(f"Baseline accuracy: {baseline_results['accuracy']:.2%}")
print(f"Optimized accuracy: {optimized_results['accuracy']:.2%}")
```

---

## 📚 **See Also**

- **MLflow GEPA Docs**: https://mlflow.org/docs/latest/genai/prompt-registry/optimize-prompts/
- **DSPy Optimizer**: For task-specific prompt optimization
- **TextGrad Optimizer**: For system prompt optimization
- **Evaluation Harness**: docs/EVALUATION_GUIDE.md
- **Prompt Registry**: docs/PROMPT_MANAGEMENT.md

---

**GEPA is now integrated and ready to optimize your agents!** 🚀
