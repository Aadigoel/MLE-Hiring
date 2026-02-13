# Merchant Underwriting Pipeline & Risk Report

A production-style machine learning pipeline for BNPL merchant underwriting that ingests data from multiple sources, trains a risk model, and generates LLM-powered underwriting reports.

## Overview

This project implements an end-to-end merchant underwriting pipeline for a Buy Now Pay Later (BNPL) platform. It combines data from five sources:

1. **Simulated Internal API** – Custom mock API returning internal risk flags and transaction summaries
2. **REST Countries API** – Enriches merchant data with country/region information
3. **Companies House API** (optional) – UK company profile data
4. **CSV Data** – Primary merchant dataset with transaction and dispute history
5. **Web Scraping** – Extracts company information from claritypay.com
6. **PDF Processing** – Async extraction of merchant terms/summaries

The pipeline collates this data into a unified view, engineers features, trains a risk classification model, aggregates portfolio-level risk, and generates a structured underwriting report via LLM.

## Quick Start

### Prerequisites
- Python 3.9+
- `pip` or `conda`

### Installation

1. **Clone and navigate to project:**
   ```bash
   cd MLE-Hiring
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # - OPENAI_API_KEY (required for LLM report generation)
   # - COMPANIES_HOUSE_API_KEY (optional; for UK company data)
   ```

### Running the Pipeline

1. **Start the simulated API (in terminal window 1):**
   ```bash
   python -m uvicorn ingestion.simulated_api:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Run the full pipeline (in terminal window 2):**
   ```bash
   python pipeline.py
   ```

   This will:
   - Ingest data from all five sources
   - Validate and collate data
   - Engineer features
   - Train a risk model
   - Generate portfolio-level risk metrics
   - Output an LLM-generated underwriting report

3. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

## Project Structure

```
MLE-Hiring/
├── data/                          # Data sources
│   ├── merchants.csv             # Primary merchant dataset
│   ├── simulated_api_contract.json
│   ├── simulated_api_example_response.json
│   └── sample_merchant_summary.pdf
├── ingestion/                     # Data ingestion modules
│   ├── __init__.py
│   ├── csv_loader.py             # CSV ingestion with validation
│   ├── api_client.py             # REST Countries & Companies House clients
│   ├── pdf_processor.py          # Async PDF extraction
│   ├── web_scraper.py            # Claritypay.com scraper
│   ├── simulated_api.py          # Mock internal API (FastAPI)
│   └── validators.py             # Pydantic schema validators
├── features/                      # Feature engineering
│   ├── __init__.py
│   └── feature_builder.py        # Feature derivation & transformations
├── model/                         # Model training & portfolio aggregation
│   ├── __init__.py
│   ├── model_trainer.py          # Risk model training & evaluation
│   └── portfolio.py              # Portfolio-level risk aggregation
├── reporting/                     # LLM reporting
│   ├── __init__.py
│   └── llm_reporter.py           # LLM prompt & report generation
├── tests/                         # Unit and integration tests
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_csv_loader.py
│   └── test_feature_builder.py
├── docs/                          # Documentation
│   └── AI_USAGE.md               # AI usage and prompts
├── pipeline.py                    # Main orchestration script
├── config.py                      # Configuration management
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── README.md                      # Original README
└── README_ASSIGNMENT.md           # Assignment details

```

## Key Implementation Details

### Configuration Management
Environment variables are managed via the `config.py` module using Pydantic Settings. See `.env.example` for required and optional variables.

### Data Validation
All ingested data is validated using Pydantic models in `ingestion/validators.py`. Invalid rows are logged and either rejected or flagged for manual review.

### Idempotency
The pipeline maintains state through logging and can be made idempotent by:
- Adding unique ingestion IDs to prevent duplicate processing
- Implementing a state database to track processed batches
- Using idempotent merge/update operations (documented in code)

### Logging
Comprehensive logging is configured throughout the pipeline. Check logs for:
- Data source failures
- Validation errors
- Feature engineering decisions
- Model metrics

### Async PDF Processing
PDF ingestion is implemented as an async operation using Python's `asyncio`. In production, this would be delegated to a task queue (e.g., Celery + Redis).

### Model Development
The risk model uses scikit-learn with a standard train/eval split. Features are normalized, and the model is evaluated on held-out test data. Portfolio aggregation provides expected high-risk count and expected loss metrics.

### LLM Report Generation
The underwriting report is generated by an LLM (OpenAI GPT-4 by default) using structured prompts. Key prompts are documented in `docs/AI_USAGE.md`.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for LLM report generation |
| `COMPANIES_HOUSE_API_KEY` | No | Companies House API key (optional; if not provided, UK data is skipped) |
| `SIMULATED_API_BASE_URL` | Yes | URL of the mock API (default: `http://localhost:8000`) |
| `REST_COUNTRIES_BASE_URL` | No | Base URL for REST Countries API |
| `LOG_LEVEL` | No | Logging level (default: `INFO`) |
| `RANDOM_SEED` | No | Random seed for reproducibility (default: `42`) |
| `TEST_SIZE` | No | Train/test split ratio (default: `0.2`) |

## Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run a specific test file
pytest tests/test_validators.py -v

# Run with coverage
pytest tests/ --cov=ingestion --cov=features --cov=model
```

## Troubleshooting

### Simulated API not accessible
- Ensure the FastAPI server is running: `python -m uvicorn ingestion.simulated_api:app --reload`
- Check that `SIMULATED_API_BASE_URL` in `.env` matches your server URL

### Missing API Keys
- For REST Countries: No key required; if rate limits hit, consider adding caching
- For Companies House: Register at https://developer.company-information.service.gov.uk/get-started (free tier available)
- For OpenAI: Get key from https://platform.openai.com/api-keys

### PDF extraction issues
- Verify `data/sample_merchant_summary.pdf` exists
- If PDF is scanned/image-based, consider using OCR (not implemented by default)

## Additional Documentation

See `docs/AI_USAGE.md` for:
- AI models and APIs used
- Key prompts and conversations
- Design rationale
- Production hardening notes

## Notes for Production

1. **Monitoring:** Implement monitoring for pipeline failures, schema drift, and model performance degradation
2. **Retraining:** Set up automated retraining triggers based on data drift or performance metrics
3. **Governance:** Add audit logging for all decisions and model outputs
4. **Data Quality:** Implement Great Expectations or similar for continuous data validation
5. **Scalability:** Replace async PDF processing with a proper task queue (Celery + Redis)
6. **Caching:** Add caching for external API calls (REST Countries, Companies House) to reduce latency
7. **Model Versioning:** Implement model registry to version and rollback models as needed

---

**Time Budget:** ~8 hours  
**Role:** Machine Learning Engineer (BNPL / Merchant Underwriting)

For questions or issues, refer to the assignment details in `README_ASSIGNMENT.md`.
