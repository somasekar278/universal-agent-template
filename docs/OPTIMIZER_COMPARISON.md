# Optimizer Comparison: DSPy vs GEPA vs TextGrad

**Choosing the right optimizer for your use case.**

---

## 📊 **Quick Decision Matrix**

| Your Situation | Use This |
|----------------|----------|
| Building a new classification agent | **DSPy** |
| Optimizing production agent with real data | **GEPA** |
| Tuning system prompt tone/style | **TextGrad** |
| Multi-step reasoning workflow | **DSPy** or **GEPA** |
| Have lots of labeled training data | **DSPy** |
| Have production usage logs | **GEPA** |
| Need to switch models (GPT-5 → GPT-5-mini) | **GEPA** |
| Optimizing multiple prompts together | **GEPA** |

---

## 🔍 **Detailed Comparison**

### **DSPy: Programmatic & Compositional**

**Philosophy:** Define what you want, DSPy figures out how.

**Approach:**
- You define **signatures** (input/output types)
- You compose **modules** (ChainOfThought, ReAct)
- DSPy **compiles** optimal prompts for your pipeline
- Uses few-shot learning + bootstrapping

**Best For:**
- ✅ Structured tasks (classification, QA, extraction)
- ✅ Multi-step reasoning (plan → execute → verify)
- ✅ When you can define clear signatures
- ✅ Rapid prototyping from scratch
- ✅ Research & experimentation

**Example:**
```python
import dspy

# Define signature
class QA(dspy.Signature):
    question = dspy.InputField()
    answer = dspy.OutputField()

# Use module
qa = dspy.ChainOfThought(QA)

# DSPy optimizes the prompts inside
result = qa(question="What is 2+2?")
```

**When NOT to use:**
- You have existing non-DSPy production code you don't want to rewrite
- Your task doesn't fit structured signatures
- You need to optimize arbitrary Python functions (use MLflow GEPA)

**Production Use:**
- ✅ Can read MLflow scorers/evals for automated optimization
- ✅ Can push optimized prompts to UC prompt registry
- ✅ Supports continuous improvement pipelines

---

### **GEPA: LLM-Driven Reflection**

**Philosophy:** Show me what you have, I'll improve it.

**Approach:**
- You have an **existing agent function**
- You have **real usage data** (inputs + expected outputs)
- GEPA uses an LLM to **reflect** on failures
- Iteratively **edits** prompts to improve performance

**Best For:**
- ✅ Production agents with usage data
- ✅ Optimizing existing code (no rewrite)
- ✅ Multi-prompt optimization
- ✅ Model migration (GPT-5 → GPT-5-mini)
- ✅ Framework-agnostic (works with ANY code)
- ✅ Continuous improvement from logs

**Example:**
```python
import mlflow
from optimization import GepaOptimizer

# Your existing agent (ANY framework)
def my_agent(question: str) -> str:
    prompt = mlflow.genai.load_prompt("prompts:/qa/1")
    return llm.call(prompt.format(question=question))

# Real usage data
train_data = [
    {"inputs": {"question": "..."}, "expectations": {"expected_response": "..."}}
]

# Optimize (no code changes!)
optimizer = GepaOptimizer()
result = optimizer.optimize(
    predict_fn=my_agent,
    train_data=train_data,
    prompt_uris=["prompts:/qa/1"]
)
```

**When NOT to use:**
- You're starting from scratch (use DSPy first)
- You don't have real usage data
- You want programmatic control over prompt structure

---

### **TextGrad: Gradient-Based Optimization**

**Philosophy:** Treat prompts like neural network weights.

**Approach:**
- Uses **automatic differentiation** on text
- Computes **gradients** through LLM outputs
- Updates prompts via **gradient descent**
- Best for continuous optimization

**Best For:**
- ✅ System prompt optimization (tone, style)
- ✅ Constraint satisfaction (length, format)
- ✅ Fine-grained prompt tuning
- ✅ Research applications

**Example:**
```python
from optimization import TextGradOptimizer

optimizer = TextGradOptimizer()
result = optimizer.optimize(
    system_prompt="You are helpful",
    evaluation_data=test_cases,
    objective="Be professional and concise"
)
```

**When NOT to use:**
- Task-specific prompts (use DSPy)
- Production optimization with logs (use GEPA)

---

## 🆚 **Head-to-Head: DSPy vs GEPA**

### **Scenario 1: Building a New Agent**

**Task:** Create a fraud detection agent from scratch.

**DSPy Approach:**
```python
class FraudDetection(dspy.Signature):
    transaction = dspy.InputField(desc="Transaction details")
    is_fraud = dspy.OutputField(desc="Boolean: fraud or not")
    reasoning = dspy.OutputField(desc="Explanation")

# DSPy handles prompt engineering
agent = dspy.ChainOfThought(FraudDetection)
```

**Winner:** **DSPy** ✅
- You're building from scratch
- Clear signature definition
- DSPy optimizes everything automatically

---

### **Scenario 2: Optimizing Production Agent**

**Task:** Your deployed agent is making mistakes. You have 10,000 logs.

**GEPA Approach:**
```python
# Convert logs to training data
train_data = [
    {
        "inputs": {"transaction": log.input},
        "expectations": {"expected_response": correct_label}
    }
    for log in production_logs
]

# Optimize existing agent (no code changes!)
result = optimizer.optimize_with_gepa(
    predict_fn=your_existing_agent,
    train_data=train_data,
    prompt_uris=["prompts:/fraud_detector/1"]
)
```

**Winner:** **GEPA** ✅
- Works with existing code
- Uses real production data
- No framework rewrite needed

---

### **Scenario 3: Multi-Step Reasoning**

**Task:** Plan → Research → Answer workflow.

**DSPy Approach:**
```python
class RAG(dspy.Module):
    def __init__(self):
        self.planner = dspy.ChainOfThought("question -> plan")
        self.researcher = dspy.Retrieve(k=5)
        self.answerer = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        plan = self.planner(question=question)
        docs = self.researcher(query=plan.plan)
        return self.answerer(context=docs, question=question)
```

**GEPA Approach:**
```python
# Register multiple prompts
plan_prompt = mlflow.genai.register_prompt(...)
answer_prompt = mlflow.genai.register_prompt(...)

# Optimize both together
result = optimizer.optimize_with_gepa(
    predict_fn=multi_step_agent,
    prompt_uris=[plan_prompt.uri, answer_prompt.uri],
    train_data=data
)
```

**Winner:** **Tie** - Both work well
- **DSPy:** Better for new development
- **GEPA:** Better for optimizing existing

---

### **Scenario 4: Model Migration**

**Task:** Switch from GPT-5 to GPT-5-mini to save costs.

**DSPy Approach:**
```python
# Need to recompile with new LLM
dspy.settings.configure(lm=gpt5_mini)
optimizer = dspy.BootstrapFewShot()
optimized = optimizer.compile(agent, trainset=data)
```

**GEPA Approach:**
```python
# Use GPT-5 outputs as expectations
train_data = [
    {
        "inputs": {"question": q},
        "expectations": {"expected_response": gpt5_output}
    }
]

# Optimize prompts for GPT-5-mini
result = optimizer.optimize_with_gepa(
    predict_fn=gpt5_mini_agent,
    train_data=train_data,
    prompt_uris=["prompts:/qa/1"]
)
```

**Winner:** **GEPA** ✅
- Designed specifically for model migration
- Learns to match GPT-5 quality with cheaper model
- Framework-agnostic

---

## 🔄 **Using Both Together**

**Best Practice:** Start with DSPy, optimize with GEPA.

### **Workflow:**

```python
# 1. Build with DSPy
import dspy

class MyAgent(dspy.Module):
    def __init__(self):
        self.qa = dspy.ChainOfThought("question -> answer")

    def forward(self, question):
        return self.qa(question=question)

# Compile with DSPy
optimizer = dspy.BootstrapFewShot()
compiled_agent = optimizer.compile(MyAgent(), trainset=initial_data)

# 2. Deploy to production
# ... collect usage data ...

# 3. Optimize with GEPA using production data
from optimization import GepaOptimizer

# Extract prompts to MLflow Registry
prompt = mlflow.genai.register_prompt(
    name="dspy_qa",
    template=compiled_agent.qa.prompt_template  # DSPy's optimized prompt
)

# Further optimize with GEPA
gepa_result = GepaOptimizer().optimize(
    predict_fn=compiled_agent,
    train_data=production_logs,
    prompt_uris=[prompt.uri]
)
```

**Benefits:**
- ✅ DSPy gives you a great starting point
- ✅ GEPA continuously improves from real data
- ✅ Best of both worlds

---

## 📈 **Performance Characteristics**

| Metric | DSPy | GEPA | TextGrad |
|--------|------|------|----------|
| **Initial Setup Time** | Medium | Low | Medium |
| **Optimization Time** | Fast | Slow | Medium |
| **Data Requirements** | 50-500 examples | 100-1000 examples | 20-100 examples |
| **Code Changes Required** | High (rewrite) | Low (none) | Medium |
| **Framework Lock-in** | Yes | No | No |
| **Multi-prompt Support** | Yes | Yes | Limited |
| **Production Ready** | Needs wrapping | Native | Needs wrapping |

---

## 💡 **Recommendations**

### **Use DSPy GEPA when:**
- ✅ Using DSPy modules (ChainOfThought, ReAct, etc.)
- ✅ Task fits structured signatures
- ✅ Want programmatic control over prompt structure
- ✅ Automated production optimization with DSPy programs
- ✅ Reading from MLflow scorers/evals for continuous improvement
- ✅ Pushing optimized prompts to UC prompt registry

### **Use MLflow GEPA when:**
- ✅ Have ANY Python function (not DSPy)
- ✅ Framework-agnostic agents (LangChain, custom code, etc.)
- ✅ Can't/won't rewrite existing code to DSPy
- ✅ Want simplest integration with Databricks
- ✅ Optimizing from production logs without code changes
- ✅ Multi-prompt optimization across different frameworks

### **Use TextGrad when:**
- ✅ Optimizing system prompts
- ✅ Tuning tone/style/constraints
- ✅ Fine-grained prompt control
- ✅ Research applications

### **Use All Three:**
1. **DSPy GEPA:** Build and continuously optimize DSPy agents (dev + production)
2. **TextGrad:** Tune system prompts for tone/style
3. **MLflow GEPA:** Optimize non-DSPy agents from production data

---

## 🎯 **For Your L1/L2 Agents**

### **L1 Chatbot:**

**Phase 1 - Development:**
```python
# Use DSPy if building from scratch
class Chatbot(dspy.Module):
    def __init__(self):
        self.chat = dspy.ChainOfThought("message -> response")
```

**Phase 2 - Production:**
```python
# Use GEPA to optimize from real conversations
result = optimizer.optimize_with_gepa(
    predict_fn=l1_agent,
    train_data=conversation_logs,
    prompt_uris=["prompts:/l1_system/1"]
)
```

### **L2 with Memory:**

**Multi-prompt optimization with GEPA:**
```python
# Optimize both retrieval and generation prompts
result = optimizer.optimize_with_gepa(
    predict_fn=l2_agent,
    prompt_uris=[
        "prompts:/l2_retrieval/1",
        "prompts:/l2_generation/1"
    ],
    train_data=conversation_logs
)
```

---

## 📚 **Summary**

| Question | Answer |
|----------|--------|
| **What's the main difference?** | DSPy GEPA = DSPy programs, MLflow GEPA = any function |
| **Which is more powerful?** | Depends on your use case |
| **Can I use both?** | Yes! They complement each other |
| **Which for production?** | Both! DSPy GEPA for DSPy agents, MLflow GEPA for others |
| **Can DSPy do production optimization?** | Yes! Via MLflow scorers/evals + UC registry |
| **Which is framework-agnostic?** | MLflow GEPA |
| **Which needs less code changes?** | MLflow GEPA (zero changes to existing functions) |

---

**Both are excellent tools. Choose based on your situation, or use both for maximum benefit!** 🚀
