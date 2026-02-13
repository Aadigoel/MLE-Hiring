# AI Usage Documentation

This document tracks how AI was used in the development of this merchant underwriting pipeline, including models, prompts, and design decisions.

## Overview

This project uses AI in two main areas:
1. **Development & Architecture** – Using Claude to design the system architecture, generate code templates, and structure the project
2. **Report Generation** – Using OpenAI's GPT-4 to generate underwriting reports from structured data

---

## AI Models Used

### 1. Claude (Development & Architecture)
**Model:** Claude 3 Haiku  
**Provider:** Anthropic  
**Purpose:** Code generation, project structure, module design  
**Usage:**
- Designed overall pipeline architecture
- Generated module templates and boilerplate code
- Structured Pydantic validators for data schemas
- Created feature engineering logic
- Designed model training and evaluation approach

### 2. OpenAI GPT-4 (Report Generation)
**Model:** GPT-4  
**Provider:** OpenAI  
**Purpose:** Generate underwriting reports from pipeline outputs  
**Configuration:**
- Model: `gpt-4` (configurable in code)
- Max tokens: 2000
- Temperature: Default (0.7)

---

## Key Prompts Used

### 1. Report Generation System Prompt
```
You are an expert BNPL underwriting analyst. 
Generate a concise (1-2 page) underwriting report for the risk team summarizing:
1. Portfolio overview and key metrics
2. Merchant risk profile by risk band
3. Key risk factors and red flags
4. Recommended actions
Be precise, actionable, and professional.
```

### 2. Report Generation User Prompt
```
Generate an underwriting report based on this data:

[Portfolio metrics, merchant summaries, model outputs in JSON]

Focus on:
- Key risk factors driving high-risk classifications
- Geographic and sector trends
- Portfolio diversification
- Recommended underwriting actions
```

---

## Design Decisions & AI Involvement

### 1. Modular Architecture
**Decisions:** Split pipeline into ingestion, features, model, reporting modules  
**AI Involvement:** Claude suggested this separation of concerns for maintainability and testability

### 2. Feature Engineering Approach
**Decisions:**
- Dispute rate as primary risk indicator
- Volume bands and transaction frequency as proxy features
- Geographic and company status risk factors
- Volume velocity to detect anomalies

**AI Involvement:** Claude helped design these features based on BNPL underwriting principles

### 3. Model Selection
**Decisions:** Use logistic regression for interpretability  
**AI Involvement:** Claude explained the trade-off between accuracy and interpretability; logistic regression chosen for production underwriting use

### 4. Validation Strategy
**Decisions:** Pydantic models for all data schemas  
**AI Involvement:** Claude generated validation templates and error handling patterns

### 5. Async PDF Processing
**Decisions:** Implement async PDF extraction with notes on production migration to task queue  
**AI Involvement:** Claude explained async patterns and provided implementation template

---

## Production Considerations Discussed with AI

1. **Monitoring & Alerts:** Implement monitoring for schema drift, model performance degradation
2. **Model Versioning:** Add model registry for versioning and rollback
3. **Data Quality:** Use Great Expectations for continuous validation
4. **Scalability:** Replace async functions with proper task queues (Celery + Redis)
5. **Caching:** Add caching layer for REST Countries and Companies House APIs
6. **Audit Logging:** Complete audit trails for all underwriting decisions
7. **Retraining:** Implement automated retraining based on data drift detection

---

## Conversations Summary

### Phase 1: Architecture Design
- **Conversation:** Discussed project structure, module separation, data flow
- **Output:** Project directory structure, core module templates

### Phase 2: Module Implementation
- **Conversation:** Designed validators, API clients, data loaders
- **Output:** Pydantic models, CSV loader, API client structure

### Phase 3: Feature Engineering
- **Conversation:** Defined features for risk modeling, explained BNPL concepts
- **Output:** FeatureBuilder class with dispute rate, volume bands, geographic factors

### Phase 4: Model Development
- **Conversation:** Selected logistic regression for interpretability
- **Output:** RiskModelTrainer with train/eval split, evaluation metrics

### Phase 5: LLM Integration
- **Conversation:** Designed prompts for report generation
- **Output:** LLMReporter class with structured prompt templates

### Phase 6: Testing & Documentation
- **Conversation:** Designed test structure and validation patterns
- **Output:** Test fixtures, test cases, documentation templates

---

## Ethical Considerations

1. **Model Interpretability:** Logistic regression chosen specifically for transparency; easier to explain decisions to merchants and regulators
2. **Bias Awareness:** Geographic risk factors documented as proxies; in production, would audit for cultural/economic bias
3. **Data Privacy:** Pipeline designed to minimize PII retention; all external APIs called respectfully
4. **Transparency:** LLM prompts documented and reproducible; no hidden decision-making

---

## Trade-offs & Alternatives Considered

| Aspect | Chosen | Alternative |
|--------|--------|-------------|
| Model Type | Logistic Regression | Random Forest (faster but less interpretable) |
| Feature Scaling | StandardScaler | MinMaxScaler (minimal impact) |
| Report Generation | OpenAI GPT-4 | Claude API or local LLM |
| Async Processing | AsyncIO | Celery (overkill for this scope) |
| Data Validation | Pydantic | JSON Schema (less Pythonic) |

---

## Future AI Enhancements

1. **Few-shot Learning:** Use LLM with examples of good/bad merchant profiles
2. **Multi-modal Analysis:** Extend to analyze merchant websites, social media
3. **Automated Feature Selection:** Use LLM to suggest relevant features from data
4. **Natural Language Underwriting Rules:** Allow analysts to write rules in plain English
5. **Anomaly Detection:** Use LLM to identify and explain unusual merchant patterns

---

## Notes for Reviewer

- All AI-assisted code has been reviewed and tested
- Prompts are designed for reproducibility and can be adjusted for different use cases
- The pipeline is designed to be AI-provider agnostic; can switch to Claude, Anthropic, or local LLMs
- Cost optimization: GPT-4 can be replaced with GPT-3.5-turbo for lower cost with minimal quality loss

---

**Last Updated:** February 13, 2026  
**Status:** Phase 1 Complete - Setup & Architecture
