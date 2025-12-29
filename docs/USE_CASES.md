# Use Cases - Domain Applications

This framework is **domain-agnostic** and can be applied to any use case requiring AI agent integration into existing pipelines.

---

## 🎯 Pattern Overview

### **The Pattern (Domain-Agnostic):**

```
Existing Pipeline
    ↓
Critical Path Processing (fast, required)
    ↓ (decision made)
Optional Agent Enrichment (inline or offline)
    ↓
Continue Pipeline
```

**Key:** Agents never block critical path. Customers control execution mode.

---

## 💼 Use Case 1: Fraud Detection (Original)

### **Domain:** Financial Services - Payment Fraud

**Existing Pipeline:**
```python
transactions = spark.table("transactions")
features = engineer_features(transactions)
fraud_scores = ml_model.predict(features)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/fraud_agents.yaml")
enriched = enrich_with_agents(fraud_scores, router)
decisions = apply_business_rules(enriched)
```

**Agents:**
- **Critical Path:** Fast ML fraud scorer (<50ms)
- **Enrichment:** Narrative generation (why fraud?), case builder, alert generator

**Value:** Human-readable fraud narratives in real-time

---

## 🏥 Use Case 2: Clinical Decision Support

### **Domain:** Healthcare - Clinical Diagnosis

**Existing Pipeline:**
```python
patient_records = spark.table("patient_records")
vitals = process_vitals(patient_records)
risk_scores = clinical_model.predict(vitals)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/clinical_agents.yaml")
enriched = enrich_with_agents(risk_scores, router)
recommendations = generate_recommendations(enriched)
```

**Agents:**
- **Critical Path:** Fast risk assessment (<50ms)
- **Enrichment:** Treatment recommendations, drug interaction checker, similar case finder

**Value:** AI-assisted clinical decision support

---

## 📞 Use Case 3: Customer Support Automation

### **Domain:** Customer Service - Ticket Routing & Response

**Existing Pipeline:**
```python
tickets = spark.table("support_tickets")
embeddings = embed_tickets(tickets)
categories = classifier.predict(embeddings)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/support_agents.yaml")
enriched = enrich_with_agents(categories, router)
responses = route_tickets(enriched)
```

**Agents:**
- **Critical Path:** Fast ticket categorization (<50ms)
- **Enrichment:** Draft responses, find KB articles, escalation recommendations

**Value:** Automated response drafts, intelligent routing

---

## 🏛️ Use Case 4: Compliance Monitoring

### **Domain:** Financial Services - AML/KYC

**Existing Pipeline:**
```python
transactions = spark.table("wire_transfers")
features = extract_features(transactions)
risk_flags = aml_model.predict(features)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/compliance_agents.yaml")
enriched = enrich_with_agents(risk_flags, router)
cases = file_sars(enriched)
```

**Agents:**
- **Critical Path:** Fast AML risk scoring (<50ms)
- **Enrichment:** SAR narrative generation, beneficial owner analysis, watchlist checking

**Value:** Automated SAR filing, narrative generation

---

## 🛡️ Use Case 5: Content Moderation

### **Domain:** Social Media - Content Safety

**Existing Pipeline:**
```python
posts = spark.table("user_posts")
embeddings = embed_content(posts)
safety_scores = safety_model.predict(embeddings)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/moderation_agents.yaml")
enriched = enrich_with_agents(safety_scores, router)
actions = apply_moderation(enriched)
```

**Agents:**
- **Critical Path:** Fast content safety classification (<50ms)
- **Enrichment:** Detailed safety analysis, context gathering, appeal preparation

**Value:** Explainable content moderation decisions

---

## 🏭 Use Case 6: Predictive Maintenance

### **Domain:** Manufacturing - Equipment Monitoring

**Existing Pipeline:**
```python
sensor_data = spark.table("equipment_sensors")
features = aggregate_metrics(sensor_data)
failure_risk = maintenance_model.predict(features)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/maintenance_agents.yaml")
enriched = enrich_with_agents(failure_risk, router)
work_orders = schedule_maintenance(enriched)
```

**Agents:**
- **Critical Path:** Fast failure prediction (<50ms)
- **Enrichment:** Root cause analysis, part recommendations, scheduling optimization

**Value:** Proactive maintenance with explanations

---

## 🎬 Use Case 7: Content Recommendation

### **Domain:** Media - Personalization

**Existing Pipeline:**
```python
user_activity = spark.table("user_events")
embeddings = create_embeddings(user_activity)
recommendations = recommender.predict(embeddings)
```

**Add Agents (3 lines):**
```python
router = AgentRouter.from_yaml("config/recsys_agents.yaml")
enriched = enrich_with_agents(recommendations, router)
personalized = apply_preferences(enriched)
```

**Agents:**
- **Critical Path:** Fast recommendation retrieval (<50ms)
- **Enrichment:** Explanation generation, diversity injection, novelty scoring

**Value:** Explainable recommendations

---

## 📊 Common Patterns Across Use Cases

### **Critical Path Pattern:**
```python
# Fast decision (<50ms)
# Always inline
# Required for operation
result = await router.route("critical_scorer", input)
```

### **Enrichment Pattern:**
```python
# Slower processing (200ms+)
# Inline or offline (customer choice)
# Adds context/explanations
if result.score > threshold:
    enrichment = await router.route("enrichment_agent", input)
```

### **Configuration Pattern:**
```yaml
agents:
  critical_scorer:
    execution_mode: "inline"    # Always inline
    timeout: 1
  
  enrichment_agent:
    execution_mode: "offline"   # Customer chooses
    timeout: 30
```

---

## 🎯 Key Takeaway

**Same framework, different domains:**

| Domain | Critical Path | Enrichment | Value |
|--------|--------------|------------|-------|
| **Fraud** | ML scorer | Narrative | Explainable decisions |
| **Healthcare** | Risk assessment | Treatment recs | Clinical support |
| **Support** | Ticket classifier | Response draft | Automation |
| **Compliance** | AML scorer | SAR narrative | Regulatory filing |
| **Moderation** | Safety classifier | Context analysis | Explainability |
| **Maintenance** | Failure predictor | Root cause | Proactive action |
| **Recommendations** | Retrieval | Explanations | User trust |

**3-line integration works for all!**

---

## 🔧 Adapting to Your Domain

### **Step 1: Define Your Data Schema**
```python
# shared/schemas/your_domain.py

class YourDomainData(BaseModel):
    """Your domain-specific data"""
    # Define your fields
```

### **Step 2: Create Your Agents**
```python
# agents/your_agents.py

class YourCriticalPathAgent(CriticalPathAgent):
    async def score(self, request):
        # Fast scoring logic
        return score

class YourEnrichmentAgent(EnrichmentAgent):
    async def enrich(self, request, score):
        # Enrichment logic
        return result
```

### **Step 3: Configure**
```yaml
# config/agents.yaml

agents:
  your_critical:
    class: "agents.YourCriticalPathAgent"
    execution_mode: "inline"
  
  your_enrichment:
    class: "agents.YourEnrichmentAgent"
    execution_mode: "offline"
```

### **Step 4: Integrate (3 lines)**
```python
router = AgentRouter.from_yaml("config/agents.yaml")
enriched = enrich_with_agents(your_data, router)
# Continue your pipeline
```

**That's it! Works for any domain.**

---

## 💡 When to Use This Pattern

### ✅ **Good Fit:**
- Existing data pipeline (Databricks Workflows, streaming, batch)
- Need AI agents for enrichment/analysis
- SLA requirements (some fast, some slow)
- Multiple agent types
- Frequent enable/disable of features
- Multi-tenant deployment

### ❌ **Not a Good Fit:**
- No existing pipeline (build from scratch)
- Single agent only (overkill)
- No SLA constraints (simpler approach works)
- Fully synchronous requirements

---

## 🚀 Getting Started

1. Choose your domain
2. Define your data schemas
3. Implement your agents (extend base classes)
4. Configure execution modes
5. Integrate (3 lines!)

**The pattern is the same across all domains!**

