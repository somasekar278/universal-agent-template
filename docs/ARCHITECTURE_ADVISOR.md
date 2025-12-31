# Architecture Advisor

**AI-powered architecture recommendations from natural language briefs**

---

## Overview

The **Architecture Advisor** (`sota-architect`) is an intelligent system that analyzes natural language use case descriptions and automatically recommends the optimal SOTA Agent Framework architecture.

**Key Features:**
- 🤖 **Natural Language Understanding** - Describe your use case in plain English
- 🎯 **Automatic Recommendations** - Get level, schemas, features, and integrations
- 📊 **Confidence Scores** - Know how confident the recommendation is
- ⏱️ **Effort Estimation** - Understand the development time required
- 🚀 **Instant Scaffolding** - Generate starter code from recommendations

---

## Quick Start

### Basic Usage

```bash
# Analyze a use case brief
sota-architect "Build a fraud detection system with memory and self-improvement"
```

### Interactive Mode

```bash
# Prompt-based interaction
sota-architect --interactive
```

### JSON Output

```bash
# Get machine-readable output
sota-architect "Simple customer support chatbot" --json
```

---

## How It Works

### 1. Complexity Analysis

The advisor analyzes your brief for complexity indicators:

| Level | Indicators | Examples |
|-------|-----------|----------|
| **Level 1** (Simple) | `chatbot`, `faq`, `basic`, `simple` | "Simple FAQ bot" |
| **Level 2** (Contextual) | `memory`, `context`, `remember`, `history` | "Chatbot that remembers conversations" |
| **Level 3** (Production) | `production`, `api`, `monitor`, `scale` | "Production API with monitoring" |
| **Level 4** (Advanced) | `plan`, `workflow`, `optimize`, `feedback` | "System that learns and improves" |
| **Level 5** (Expert) | `multi-agent`, `a2a`, `collaborate`, `enterprise` | "Multi-agent marketplace" |

### 2. Feature Detection

Automatically detects required features:

| Feature | Keywords | Auto-enabled |
|---------|----------|--------------|
| **Memory** | `memory`, `remember`, `recall` | Level 2+ |
| **LangGraph** | `plan`, `workflow`, `graph` | Level 4+ |
| **MCP** | `tool`, `external`, `mcp` | On mention |
| **A2A** | `a2a`, `multi-agent`, `cross-framework` | On mention |
| **Monitoring** | `monitor`, `observability`, `telemetry` | Level 3+ |
| **Optimization** | `optimize`, `improve`, `tune` | On mention |
| **Databricks** | `databricks`, `unity catalog`, `mlflow` | On mention |

### 3. Domain Detection

Recognizes common domains:
- **Fraud Detection** - `fraud`, `risk`, `scam`
- **Customer Support** - `support`, `helpdesk`, `ticket`
- **Analytics** - `analytics`, `insights`, `data`
- **Healthcare** - `health`, `medical`, `patient`
- **Finance** - `finance`, `banking`, `trading`
- **E-commerce** - `ecommerce`, `shopping`, `cart`
- **HR** - `hr`, `recruiting`, `hiring`
- **Legal** - `legal`, `contract`, `compliance`

### 4. Schema Recommendation

Automatically selects appropriate schemas:

| Level | Input Schema | Output Schema | Use Case |
|-------|-------------|---------------|----------|
| 1 | `ChatInput` | `ChatOutput` | Simple chatbots |
| 2 | `ContextAwareInput` | `ContextAwareOutput` | With memory |
| 3 | `APIRequest` | `APIResponse` | Production APIs |
| 4 | `WorkflowInput` | `WorkflowOutput` | Complex workflows |
| 5 | `CollaborationRequest` | `CollaborationResponse` | Multi-agent |

---

## Examples

### Example 1: Simple Chatbot

**Brief:**
```bash
sota-architect "Build a simple customer support chatbot to answer FAQ questions"
```

**Recommendation:**
```
📊 Recommended Level: Level 1: Simple Chatbot
   Confidence: 100%

📋 Schemas:
   Input:  ChatInput
   Output: ChatOutput

💡 Reasoning:
   Based on your requirements, a simple chatbot architecture is sufficient.
   Detected domain: Customer Support

⏱️  Estimated Effort: 2-4 hours

🚀 Next Steps:
   1. Run: sota-learn start 1
   2. Or: sota-generate customer_support_bot --level 1
   3. Enable features as needed
```

### Example 2: Context-Aware System

**Brief:**
```bash
sota-architect "Healthcare assistant that remembers patient history and personalizes responses"
```

**Recommendation:**
```
📊 Recommended Level: Level 2: Context-Aware Agent
   Confidence: 90%

📋 Schemas:
   Input:  ContextAwareInput
   Output: ContextAwareOutput

✨ Core Features:
   • memory

💡 Reasoning:
   Your use case requires context awareness and memory capabilities.
   Detected domain: Healthcare
   Required features: memory

⏱️  Estimated Effort: 4-8 hours
```

### Example 3: Production API

**Brief:**
```bash
sota-architect "Production-grade analytics API with monitoring and health checks for enterprise deployment"
```

**Recommendation:**
```
📊 Recommended Level: Level 3: Production API
   Confidence: 95%

📋 Schemas:
   Input:  APIRequest
   Output: APIResponse

✨ Core Features:
   • memory
   • monitoring

🔌 Integrations:
   • (None explicitly required)

💡 Reasoning:
   This is a production-grade system requiring robust API design and monitoring.
   Detected domain: Analytics
   Required features: memory, monitoring

⏱️  Estimated Effort: 8-16 hours
```

### Example 4: Complex Workflow

**Brief:**
```bash
sota-architect "Fraud detection system that plans investigations, learns from feedback, and improves over time"
```

**Recommendation:**
```
📊 Recommended Level: Level 4: Complex Workflow
   Confidence: 100%

📋 Schemas:
   Input:  WorkflowInput
   Output: WorkflowOutput

✨ Core Features:
   • optimization
   • memory
   • monitoring
   • langgraph

🔌 Integrations:
   • LangGraph

💡 Reasoning:
   This is a complex workflow requiring planning, execution, and self-improvement loops.
   Detected domain: Fraud
   Required features: optimization, memory, monitoring, langgraph
   Recommended integrations: LangGraph

⏱️  Estimated Effort: 16-40 hours
```

### Example 5: Multi-Agent System

**Brief:**
```bash
sota-architect "Enterprise multi-agent system with A2A protocol for cross-framework collaboration and Databricks integration"
```

**Recommendation:**
```
📊 Recommended Level: Level 5: Multi-Agent System
   Confidence: 100%

📋 Schemas:
   Input:  CollaborationRequest
   Output: CollaborationResponse

✨ Core Features:
   • mcp
   • a2a
   • databricks
   • memory
   • monitoring
   • langgraph
   • optimization
   • benchmarking

🔌 Integrations:
   • MCP
   • A2A
   • Databricks
   • LangGraph

💡 Reasoning:
   This is an expert-level multi-agent system requiring advanced collaboration.
   Required features: mcp, a2a, databricks, memory, monitoring, langgraph, optimization, benchmarking
   Recommended integrations: MCP, A2A, Databricks, LangGraph

⏱️  Estimated Effort: 32-80 hours
```

---

## Advanced Usage

### JSON Output for Automation

```bash
# Get JSON output
sota-architect "Financial trading bot" --json

# Output:
{
  "level": 3,
  "level_name": "Level 3: Production API",
  "confidence": 0.8,
  "input_schema": "APIRequest",
  "output_schema": "APIResponse",
  "features": ["memory", "monitoring"],
  "integrations": [],
  "reasoning": "...",
  "estimated_hours": "8-16 hours",
  "generation_params": {
    "level": 3,
    "domain": "finance",
    "features": {
      "memory": true,
      "langgraph": false,
      "mcp": false,
      "a2a": false,
      "monitoring": true,
      "optimization": false,
      "benchmarking": false,
      "databricks": false
    },
    "schemas": {
      "input": "APIRequest",
      "output": "APIResponse"
    }
  }
}
```

### Integration with Other Tools

```bash
# 1. Get recommendation
sota-architect "Healthcare diagnostic assistant" --json > recommendation.json

# 2. Extract level
LEVEL=$(cat recommendation.json | jq -r '.level')

# 3. Generate project with recommended level
sota-learn start $LEVEL

# 4. Or use sota-generate
sota-generate healthcare_assistant --level $LEVEL
```

---

## Confidence Scores

The advisor provides confidence scores (0-100%) based on:

- **100%**: Clear indicators, high certainty
- **80-99%**: Strong indicators, good confidence
- **60-79%**: Moderate indicators, reasonable confidence
- **40-59%**: Weak indicators, consider manual review
- **< 40%**: Unclear requirements, recommend interactive mode

**Tips for higher confidence:**
- Be specific about requirements
- Mention key features explicitly (`memory`, `planning`, `multi-agent`)
- Include domain context
- Describe scale and complexity

---

## Customization

### For Framework Developers

Extend the advisor by modifying `sota_agent/architect.py`:

```python
from sota_agent.architect import ArchitectureAdvisor

# Create custom advisor
advisor = ArchitectureAdvisor()

# Add custom patterns
advisor.complexity_patterns[ComplexityLevel.EXPERT].extend([
    r'\bmassive.?scale\b',
    r'\bglobal\b'
])

# Analyze
recommendation = advisor.analyze_brief("Your brief here")
```

---

## Comparison with Other Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| **sota-architect** | Architecture recommendation | Natural language brief | Level + features + schemas |
| **sota-setup** | Interactive wizard | User answers questions | Feature selection |
| **sota-advisor** | Project analysis | Existing project path | Recommendations |
| **sota-learn** | Guided learning | Level selection | Learning project |
| **sota-generate** | Project generation | Project name + params | Full project |

**When to use `sota-architect`:**
- ✅ Starting a new project
- ✅ Unsure which level to use
- ✅ Want automated recommendations
- ✅ Need to explain architecture to stakeholders

**When to use other tools:**
- `sota-setup`: Want interactive guidance
- `sota-advisor`: Have existing code to analyze
- `sota-learn`: Want step-by-step learning
- `sota-generate`: Know exactly what you need

---

## Limitations

### Current Limitations

1. **Pattern-based** - Uses regex patterns, not true NLP
2. **English only** - Currently only supports English
3. **Limited domain knowledge** - May not recognize niche domains
4. **No cost analysis** - Doesn't estimate infrastructure costs

### Future Enhancements

- [ ] LLM-powered analysis (GPT-4, Claude)
- [ ] Multi-language support
- [ ] Cost estimation (compute, storage, API calls)
- [ ] Team size recommendations
- [ ] Technology stack suggestions
- [ ] Deployment strategy recommendations
- [ ] Security assessment
- [ ] Compliance checking

---

## Troubleshooting

### Low Confidence Scores

**Problem:** Confidence < 60%

**Solutions:**
1. Be more specific in your brief
2. Mention key features explicitly
3. Use interactive mode: `sota-architect --interactive`
4. Combine with `sota-setup` for guided experience

### Unexpected Level Recommendation

**Problem:** Recommended level doesn't match expectations

**Solutions:**
1. Check the reasoning section
2. Verify feature requirements in your brief
3. Manually specify level: `sota-learn start <level>`
4. Use `sota-setup` for more control

### Missing Features

**Problem:** Required feature not detected

**Solutions:**
1. Mention feature explicitly in brief (`memory`, `A2A`, etc.)
2. Use JSON output to see what was detected
3. Manually enable features after generation
4. File an issue for pattern improvements

---

## Best Practices

### Writing Good Briefs

✅ **Good:**
- "Build a customer support chatbot with conversation memory and sentiment analysis"
- "Production fraud detection API with real-time monitoring and self-improvement"
- "Multi-agent healthcare system using A2A protocol and Databricks"

❌ **Bad:**
- "Make an agent" (too vague)
- "AI thing" (no specifics)
- "System" (no requirements)

### Key Elements to Include

1. **Domain/Purpose** - What is it for?
2. **Key Features** - Memory? Planning? Multi-agent?
3. **Scale** - Production? Prototype? Enterprise?
4. **Special Requirements** - A2A? Databricks? MCP?

---

## Examples by Domain

### Customer Support
```bash
sota-architect "Customer support agent with ticket classification, sentiment analysis, and automated responses"
```

### Healthcare
```bash
sota-architect "Medical diagnosis assistant that remembers patient history and provides personalized recommendations"
```

### Finance
```bash
sota-architect "Trading bot with market analysis, risk assessment, and portfolio optimization using real-time data"
```

### E-commerce
```bash
sota-architect "Product recommendation engine with personalization, A/B testing, and performance monitoring"
```

### Legal
```bash
sota-architect "Contract analysis system with clause extraction, risk scoring, and compliance checking"
```

---

## Related Documentation

- **[LEARNING_PATH.md](LEARNING_PATH.md)** - Detailed breakdown of each level
- **[LEARNING_SCHEMAS.md](LEARNING_SCHEMAS.md)** - Schema specifications
- **[FEATURE_SELECTION.md](FEATURE_SELECTION.md)** - Manual feature selection guide
- **[USER_JOURNEY.md](USER_JOURNEY.md)** - Complete user journey paths

---

## CLI Reference

```bash
# Basic usage
sota-architect <brief>

# Flags
--interactive, -i    # Interactive mode with prompts
--json, -j           # Output as JSON

# Examples
sota-architect "Simple chatbot"
sota-architect --interactive
sota-architect "Multi-agent system" --json
```

---

**🎯 The Architecture Advisor makes it easy to go from idea to implementation in seconds!**

