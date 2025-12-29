# Cross-Domain Examples

**Real-world examples showing how to use SOTA Agent Framework as a template for different domains.**

## Table of Contents
1. [Fraud Detection](#1-fraud-detection-use-case)
2. [Customer Support](#2-customer-support)
3. [Content Moderation](#3-content-moderation)
4. [Healthcare Diagnosis](#4-healthcare-diagnosis)
5. [Data Quality](#5-data-quality-monitoring)
6. [E-commerce Recommendations](#6-e-commerce-recommendations)
7. [Legal Document Review](#7-legal-document-review)
8. [Security Threat Detection](#8-security-threat-detection)

---

## 1. Fraud Detection (Original Use Case)

### Domain Overview
Detect fraudulent transactions in real-time payment processing.

### Agents

```python
# fraud_agents/transaction_scorer.py
from agents import CriticalPathAgent
from shared.schemas import AgentInput

class TransactionScorer(CriticalPathAgent):
    """Fast fraud scoring - must be < 50ms."""
    
    async def score(self, request: AgentInput) -> float:
        transaction = request.data
        
        # Fast ML model (XGBoost, pre-loaded)
        features = self.extract_features(transaction)
        risk_score = self.model.predict(features)
        
        return float(risk_score)

class FraudNarrative(EnrichmentAgent):
    """Generate detailed fraud explanation."""
    
    async def enrich(self, request: AgentInput, risk_score: float) -> str:
        if risk_score < 0.7:
            return "Low risk transaction"
        
        transaction = request.data
        
        # LLM generates detailed narrative
        prompt = f"""
        Analyze this transaction for fraud:
        Amount: ${transaction.amount}
        Location: {transaction.location}
        Risk Score: {risk_score:.2f}
        
        Explain the risk factors.
        """
        
        narrative = await self.llm.generate(prompt)
        return narrative
```

### Configuration

```yaml
# config/fraud_agents.yaml
agents:
  transaction_scorer:
    class: "fraud_agents.TransactionScorer"
    execution_mode: "in_process"  # Critical path
    timeout: 0.05  # 50ms
  
  fraud_narrative:
    class: "fraud_agents.FraudNarrative"
    execution_mode: "ray_task"  # Async enrichment
    timeout: 30
    threshold: 0.7  # Only for high risk
```

### Usage

```python
from agents import AgentRouter

router = AgentRouter.from_yaml("config/fraud_agents.yaml")

# Process transaction
result = await router.route("transaction_scorer", transaction_input)
if result.risk_score > 0.7:
    narrative = await router.route("fraud_narrative", transaction_input)
```

---

## 2. Customer Support

### Domain Overview
Automatically route and respond to customer support tickets.

### Agents

```python
# support_agents/ticket_classifier.py
from agents import CriticalPathAgent, EnrichmentAgent

class TicketClassifier(CriticalPathAgent):
    """Fast ticket classification and routing."""
    
    async def score(self, request: AgentInput) -> float:
        ticket = request.data
        
        # Fast classification model
        category = self.classifier.predict(ticket.text)
        urgency = self.calculate_urgency(ticket)
        
        return urgency  # 0-1 scale

class ResponseGenerator(EnrichmentAgent):
    """Generate personalized support response."""
    
    async def enrich(self, request: AgentInput, urgency: float) -> str:
        ticket = request.data
        
        # Retrieve similar past tickets
        similar = await self.vector_search(ticket.text)
        
        # Generate response with LLM
        prompt = f"""
        Customer ticket: {ticket.text}
        Urgency: {urgency:.2f}
        Similar resolved tickets: {similar}
        
        Generate a helpful response.
        """
        
        response = await self.llm.generate(prompt)
        return response

class SentimentAnalyzer(EnrichmentAgent):
    """Analyze customer sentiment."""
    
    async def enrich(self, request: AgentInput, urgency: float) -> str:
        ticket = request.data
        
        sentiment = self.sentiment_model.analyze(ticket.text)
        emotions = self.emotion_model.detect(ticket.text)
        
        return f"Sentiment: {sentiment}, Emotions: {emotions}"
```

### Configuration

```yaml
# config/support_agents.yaml
agents:
  ticket_classifier:
    class: "support_agents.TicketClassifier"
    execution_mode: "in_process"
    timeout: 1
  
  response_generator:
    class: "support_agents.ResponseGenerator"
    execution_mode: "ray_task"
    timeout: 20
  
  sentiment_analyzer:
    class: "support_agents.SentimentAnalyzer"
    execution_mode: "ray_task"
    timeout: 5
```

### Usage

```python
# Real-time ticket processing
async def process_ticket(ticket):
    router = AgentRouter.from_yaml("config/support_agents.yaml")
    
    # Quick classification
    classification = await router.route("ticket_classifier", ticket_input)
    
    # Generate response in background
    asyncio.create_task(
        router.route("response_generator", ticket_input)
    )
    
    # Analyze sentiment
    sentiment = await router.route("sentiment_analyzer", ticket_input)
    
    return classification, sentiment
```

---

## 3. Content Moderation

### Domain Overview
Moderate user-generated content for policy violations.

### Agents

```python
# moderation_agents/content_scorer.py
from agents import CriticalPathAgent, EnrichmentAgent

class ToxicityScorer(CriticalPathAgent):
    """Fast toxicity detection."""
    
    async def score(self, request: AgentInput) -> float:
        content = request.data
        
        # Fast toxicity model (DistilBERT, optimized)
        toxicity = self.toxicity_model.score(content.text)
        
        return toxicity

class PolicyAnalyzer(EnrichmentAgent):
    """Detailed policy violation analysis."""
    
    async def enrich(self, request: AgentInput, toxicity: float) -> str:
        if toxicity < 0.8:
            return "Content appears acceptable"
        
        content = request.data
        
        # Detailed analysis with LLM
        prompt = f"""
        Content: {content.text}
        Toxicity Score: {toxicity:.2f}
        
        Analyze for policy violations:
        - Hate speech
        - Harassment
        - Violence
        - Misinformation
        
        Provide detailed explanation.
        """
        
        analysis = await self.llm.generate(prompt)
        return analysis

class ImageModerator(CriticalPathAgent):
    """Fast image content moderation."""
    
    async def score(self, request: AgentInput) -> float:
        image = request.data
        
        # Fast vision model
        scores = self.vision_model.classify(image.url)
        
        # Max of all violation scores
        return max(scores.values())
```

### Configuration

```yaml
# config/moderation_agents.yaml
agents:
  toxicity_scorer:
    class: "moderation_agents.ToxicityScorer"
    execution_mode: "in_process"
    timeout: 0.1
  
  policy_analyzer:
    class: "moderation_agents.PolicyAnalyzer"
    execution_mode: "ray_task"
    timeout: 15
    threshold: 0.8
  
  image_moderator:
    class: "moderation_agents.ImageModerator"
    execution_mode: "process_pool"
    timeout: 2
```

### Usage

```python
# Stream processing
async def moderate_content_stream():
    router = AgentRouter.from_yaml("config/moderation_agents.yaml")
    
    async for content in content_stream:
        # Fast check
        score = await router.route("toxicity_scorer", content_input)
        
        if score.risk_score > 0.8:
            # Flag for review
            await flag_for_review(content)
            
            # Detailed analysis (async)
            asyncio.create_task(
                router.route("policy_analyzer", content_input)
            )
```

---

## 4. Healthcare Diagnosis

### Domain Overview
Support medical professionals with diagnosis suggestions.

### Agents

```python
# healthcare_agents/triage_scorer.py
from agents import CriticalPathAgent, EnrichmentAgent

class TriageScorer(CriticalPathAgent):
    """Fast patient triage assessment."""
    
    async def score(self, request: AgentInput) -> float:
        symptoms = request.data
        
        # Fast triage model
        urgency = self.triage_model.assess_urgency(
            symptoms=symptoms.symptoms,
            vitals=symptoms.vitals,
            demographics=symptoms.patient_demographics
        )
        
        return urgency  # 0 = routine, 1 = critical

class DiagnosisSuggester(EnrichmentAgent):
    """Generate diagnosis suggestions."""
    
    async def enrich(self, request: AgentInput, urgency: float) -> str:
        patient_data = request.data
        
        # Retrieve similar cases
        similar_cases = await self.search_medical_db(patient_data)
        
        # Medical LLM for suggestions
        prompt = f"""
        Patient symptoms: {patient_data.symptoms}
        Vitals: {patient_data.vitals}
        Medical history: {patient_data.history}
        Urgency: {urgency:.2f}
        
        Similar cases: {similar_cases}
        
        Suggest possible diagnoses and recommended tests.
        """
        
        suggestions = await self.medical_llm.generate(prompt)
        return suggestions

class DrugInteractionChecker(EnrichmentAgent):
    """Check for drug interactions."""
    
    async def enrich(self, request: AgentInput, urgency: float) -> str:
        patient = request.data
        
        # Check interactions
        interactions = self.interaction_db.check(
            current_meds=patient.current_medications,
            proposed_meds=patient.proposed_medications
        )
        
        if interactions:
            return f"⚠️ Drug interactions detected: {interactions}"
        return "No interactions detected"
```

### Configuration

```yaml
# config/healthcare_agents.yaml
agents:
  triage_scorer:
    class: "healthcare_agents.TriageScorer"
    execution_mode: "in_process"
    timeout: 2
  
  diagnosis_suggester:
    class: "healthcare_agents.DiagnosisSuggester"
    execution_mode: "ray_task"
    timeout: 30
  
  drug_interaction_checker:
    class: "healthcare_agents.DrugInteractionChecker"
    execution_mode: "in_process"
    timeout: 1
```

### Usage

```python
# Clinical decision support
async def clinical_support(patient_data):
    router = AgentRouter.from_yaml("config/healthcare_agents.yaml")
    
    # Immediate triage
    triage = await router.route("triage_scorer", patient_input)
    
    if triage.risk_score > 0.8:
        # Critical - alert staff
        await alert_medical_staff(patient_data)
    
    # Diagnosis suggestions (async)
    diagnosis = await router.route("diagnosis_suggester", patient_input)
    
    # Drug interaction check
    interactions = await router.route("drug_interaction_checker", patient_input)
    
    return triage, diagnosis, interactions
```

---

## 5. Data Quality Monitoring

### Domain Overview
Monitor data quality and detect anomalies in data pipelines.

### Agents

```python
# data_quality_agents/anomaly_detector.py
from agents import CriticalPathAgent, EnrichmentAgent

class AnomalyDetector(CriticalPathAgent):
    """Fast anomaly detection in data streams."""
    
    async def score(self, request: AgentInput) -> float:
        data_batch = request.data
        
        # Fast anomaly detection (Isolation Forest)
        anomaly_scores = self.model.score_samples(data_batch.values)
        max_anomaly = max(abs(anomaly_scores))
        
        return float(max_anomaly)

class RootCauseAnalyzer(EnrichmentAgent):
    """Analyze root cause of data quality issues."""
    
    async def enrich(self, request: AgentInput, anomaly_score: float) -> str:
        data_batch = request.data
        
        # Statistical analysis
        stats = self.compute_statistics(data_batch)
        changes = self.detect_distribution_shifts(data_batch)
        
        # LLM explains root cause
        prompt = f"""
        Data quality issue detected:
        Anomaly score: {anomaly_score:.2f}
        Statistics: {stats}
        Distribution changes: {changes}
        
        Explain likely root causes and suggest fixes.
        """
        
        analysis = await self.llm.generate(prompt)
        return analysis

class SchemaValidator(CriticalPathAgent):
    """Validate data schema compliance."""
    
    async def score(self, request: AgentInput) -> float:
        data = request.data
        
        # Check schema compliance
        violations = self.schema_checker.validate(data)
        
        # Score based on violations
        violation_rate = len(violations) / len(data)
        return violation_rate
```

### Configuration

```yaml
# config/data_quality_agents.yaml
agents:
  anomaly_detector:
    class: "data_quality_agents.AnomalyDetector"
    execution_mode: "in_process"
    timeout: 5
  
  root_cause_analyzer:
    class: "data_quality_agents.RootCauseAnalyzer"
    execution_mode: "ray_task"
    timeout: 30
    threshold: 0.7
  
  schema_validator:
    class: "data_quality_agents.SchemaValidator"
    execution_mode: "in_process"
    timeout: 2
```

### Usage

```python
# Data pipeline monitoring
async def monitor_data_pipeline(data_batch):
    router = AgentRouter.from_yaml("config/data_quality_agents.yaml")
    
    # Quick checks
    anomaly_check = await router.route("anomaly_detector", data_input)
    schema_check = await router.route("schema_validator", data_input)
    
    if anomaly_check.risk_score > 0.7:
        # Analyze root cause
        analysis = await router.route("root_cause_analyzer", data_input)
        await alert_data_team(analysis)
    
    return anomaly_check, schema_check
```

---

## 6. E-commerce Recommendations

### Domain Overview
Personalized product recommendations and dynamic pricing.

### Agents

```python
# ecommerce_agents/recommendation_engine.py
from agents import CriticalPathAgent, EnrichmentAgent

class FastRecommender(CriticalPathAgent):
    """Fast product recommendations."""
    
    async def score(self, request: AgentInput) -> float:
        user_context = request.data
        
        # Fast collaborative filtering
        recommendations = self.cf_model.recommend(
            user_id=user_context.user_id,
            context=user_context.context,
            n=10
        )
        
        # Confidence score
        return recommendations[0].confidence

class PersonalizedNarrative(EnrichmentAgent):
    """Generate personalized product descriptions."""
    
    async def enrich(self, request: AgentInput, confidence: float) -> str:
        user_context = request.data
        
        # LLM generates personalized description
        prompt = f"""
        User profile: {user_context.preferences}
        Product: {user_context.product}
        Purchase history: {user_context.history}
        
        Generate a personalized product description that appeals to this user.
        """
        
        description = await self.llm.generate(prompt)
        return description

class DynamicPricer(CriticalPathAgent):
    """Dynamic pricing based on demand."""
    
    async def score(self, request: AgentInput) -> float:
        pricing_context = request.data
        
        # Fast pricing model
        optimal_price = self.pricing_model.predict(
            base_price=pricing_context.base_price,
            demand=pricing_context.current_demand,
            inventory=pricing_context.inventory_level,
            competitor_prices=pricing_context.competitor_prices
        )
        
        # Return price multiplier (1.0 = base price)
        return optimal_price / pricing_context.base_price
```

### Configuration

```yaml
# config/ecommerce_agents.yaml
agents:
  fast_recommender:
    class: "ecommerce_agents.FastRecommender"
    execution_mode: "in_process"
    timeout: 0.1
  
  personalized_narrative:
    class: "ecommerce_agents.PersonalizedNarrative"
    execution_mode: "ray_task"
    timeout: 10
  
  dynamic_pricer:
    class: "ecommerce_agents.DynamicPricer"
    execution_mode: "in_process"
    timeout: 0.05
```

---

## 7. Legal Document Review

### Domain Overview
Automated review of legal contracts and documents.

### Agents

```python
# legal_agents/contract_analyzer.py
from agents import CriticalPathAgent, EnrichmentAgent

class RiskScorer(CriticalPathAgent):
    """Fast contract risk assessment."""
    
    async def score(self, request: AgentInput) -> float:
        contract = request.data
        
        # Fast risk indicators
        risk_flags = self.detect_risk_clauses(contract.text)
        risk_score = len(risk_flags) / self.max_risk_flags
        
        return min(risk_score, 1.0)

class ClauseAnalyzer(EnrichmentAgent):
    """Detailed clause-by-clause analysis."""
    
    async def enrich(self, request: AgentInput, risk_score: float) -> str:
        contract = request.data
        
        # Extract and analyze clauses
        clauses = self.extract_clauses(contract.text)
        
        analyses = []
        for clause in clauses:
            prompt = f"""
            Analyze this contract clause:
            {clause}
            
            Check for:
            - Unfavorable terms
            - Legal risks
            - Missing protections
            """
            
            analysis = await self.legal_llm.generate(prompt)
            analyses.append(analysis)
        
        return "\n\n".join(analyses)
```

---

## 8. Security Threat Detection

### Domain Overview
Real-time security threat detection and response.

### Agents

```python
# security_agents/threat_detector.py
from agents import CriticalPathAgent, EnrichmentAgent

class ThreatScorer(CriticalPathAgent):
    """Fast threat detection."""
    
    async def score(self, request: AgentInput) -> float:
        event = request.data
        
        # Fast threat model (anomaly + signature)
        threat_score = self.threat_model.score(
            event_type=event.type,
            source_ip=event.source_ip,
            user=event.user,
            action=event.action
        )
        
        return threat_score

class ThreatInvestigator(EnrichmentAgent):
    """Deep threat investigation."""
    
    async def enrich(self, request: AgentInput, threat_score: float) -> str:
        event = request.data
        
        # Gather context
        related_events = await self.query_siem(event)
        threat_intel = await self.query_threat_db(event.source_ip)
        
        # LLM analyzes
        prompt = f"""
        Security event: {event}
        Threat score: {threat_score:.2f}
        Related events: {related_events}
        Threat intel: {threat_intel}
        
        Analyze and recommend response.
        """
        
        investigation = await self.security_llm.generate(prompt)
        return investigation
```

---

## Common Patterns Across All Domains

### Pattern 1: Fast + Slow
All domains use critical path (fast) + enrichment (slow) pattern.

### Pattern 2: Configuration-Driven
All use YAML config to control behavior without code changes.

### Pattern 3: Type-Safe
All use Pydantic models for data validation.

### Pattern 4: Same Base Classes
All extend `Agent`, `CriticalPathAgent`, or `EnrichmentAgent`.

### Pattern 5: Same Integration
All integrate the same way: 3 lines of code.

## Conclusion

**The SOTA Agent Framework template works for ANY domain that needs:**
- Fast decisions with optional enrichment
- LLM-powered analysis
- Configurable behavior
- Scalable execution
- Type-safe data handling

**Start with the template generator:**
```bash
python template_generator.py --domain "your_domain"
```

**Implement your logic, configure, and deploy!** 🚀

