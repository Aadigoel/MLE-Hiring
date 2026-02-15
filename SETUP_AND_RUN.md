# Setup and Run Guide: BNPL Merchant Underwriting Pipeline

This guide walks you through cloning, setting up, and running the merchant underwriting pipeline.

---

## Prerequisites

- **Python 3.11+** (tested with 3.13)
- **pip** or **conda** (for dependency management)
- **macOS/Linux/Windows** with a terminal
- **Git** installed
- *Optional*: OpenAI API key (for LLM report generation)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/Aadigoel/MLE-Hiring.git
cd MLE-Hiring
```

---

## Step 2: Create a Virtual Environment

Using `venv`:
```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# OR on Windows:
# .venv\Scripts\activate
```

Using `conda`:
```bash
conda create -n mle-hiring python=3.13
conda activate mle-hiring
```

---

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
- `scikit-learn==1.3.2` – Model training & evaluation
- `pandas==2.1.3` – Data manipulation
- `fastapi==0.104.1` – Simulated API backend
- `uvicorn==0.24.0` – ASGI server
- `PyPDF2==3.0.1` – PDF text extraction
- `openai==1.52.0` – GPT-4 report generation
- `pydantic==2.5.0` – Data validation

---

## Step 4: Configure Environment Variables (Optional)

Create a `.env` file in the project root:

```bash
touch .env
```

Add these (OpenAI key is optional; pipeline will run without it):

```
OPENAI_API_KEY=sk-your-key-here
COMPANIES_HOUSE_API_KEY=your-key-here
```

---

## Step 5: Verify Data Files

Ensure the following files exist in `data/`:

- `merchants.csv` – Base merchant data (50 merchants)
- `sample_merchant_summary.pdf` – PDF to extract text from

```bash
ls -la data/
```

---

## Step 6: Start the Simulated API (Optional but Recommended)

In a **second terminal** (keep this running):

```bash
source .venv/bin/activate  # Activate venv
uvicorn ingestion.simulated_api:app --host 127.0.0.1 --port 8000
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

**Verify it's running** (in a third terminal):
```bash
curl http://127.0.0.1:8000/health
# Should return: {"status":"ok"}
```

**Note:** The pipeline can run without the live API—it will fall back to contract mock data.

---

## Step 7: Run the Pipeline

In your **main terminal**:

```bash
python3 pipeline.py
```

The pipeline will:
1. **Phase 1:** Load merchants.csv, fetch enrichment from APIs
2. **Phase 2:** Process PDF asynchronously, collate all data
3. **Phase 3:** Engineer 10 features (avoiding data leakage)
4. **Phase 4:** Train LogisticRegression model (AUC ~0.714)
5. **Phase 5:** Generate risk predictions for all merchants
6. **Phase 6:** Aggregate portfolio-level risk metrics
7. **Phase 7:** Generate LLM-powered underwriting report (if API key provided)

**Expected output:**
```
================================================================================
MERCHANT UNDERWRITING PIPELINE
================================================================================

[PHASE 1] Ingesting data from all sources...
  ✓ Loaded 50 merchants from CSV
  ✓ Fetched API data for 9 merchants
  ✓ Enriched 50 countries
  ✓ Processed PDF (638 chars)

[PHASE 2] Engineering features for risk model...
  Target distribution: {0: 38, 1: 12}
  ✓ Engineered 10 features

[PHASE 3] Training risk classification model...
  ✓ Model trained (AUC: 0.714)
    Train size: 40, Test size: 10

[PHASE 4] Generating risk predictions...
  ✓ Generated predictions for 50 merchants

[PHASE 5] Aggregating portfolio-level risk...
  ✓ Portfolio summary:
    Total merchants: 50
    High-risk count: 8
    Expected loss: 1234567.89

[PHASE 6] Generating LLM-powered underwriting report...
  ✓ Report generated successfully

================================================================================
PIPELINE EXECUTION COMPLETE
================================================================================
```

---

## Output Files

After running the pipeline, check these files:

| File | Purpose |
|------|---------|
| `data/collated_merchants.csv` | All 50 merchants with enriched data |
| `data/collated_merchants_with_predictions.csv` | Merchants + risk probabilities |
| `data/sample_merchant_summary.txt` | Extracted PDF text |
| `data/underwriting_report.txt` | LLM-generated insights |
| `model/risk_model.pkl` | Trained model (Logistic Regression + scaler) |
| `logs/ingestion.log` | Detailed ingestion logs |

---

## Step 8: View Results

**Quick inspection:**
```bash
# See predictions for first 5 merchants
head -6 data/collated_merchants_with_predictions.csv | cut -d',' -f1,2,12

# View portfolio risk summary
tail -20 logs/ingestion.log | grep -E "Portfolio|Expected loss"

# Read generated report
cat data/underwriting_report.txt
```

---

## Running with Pipeline Output Filtering

To see only key metrics (skip verbose logs):

```bash
python3 pipeline.py 2>&1 | grep -E "Engineered|AUC|Portfolio|COMPLETE"
```

Or see the last 100 lines:
```bash
python3 pipeline.py 2>&1 | tail -100
```

---

## Running Tests

Run unit tests to verify pipeline integrity:

```bash
pytest tests/ -v
```

Key tests:
- `test_pdf_exclusion.py` – Verifies PDF text isn't in training data
- `test_feature_builder.py` – Validates feature engineering (no leakage)
- `test_validators.py` – Checks Pydantic data validation
- `test_model_trainer.py` – Tests model training & prediction

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'sklearn'`
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: `FileNotFoundError: data/merchants.csv`
**Solution:** Ensure you're in the project root, and the `data/` folder exists with test data.

### Issue: `Connection refused` when pipeline runs (but API not started)
**Solution:** This is normal—pipeline falls back to mock contract data. Start the API in a separate terminal if you want live data.

### Issue: `OpenAI API error` during report generation
**Solution:** Either set `OPENAI_API_KEY` in `.env` or ignore—report generation is optional; pipeline still completes.

### Issue: `UnicodeDecodeError` when reading PDF
**Solution:** Ensure `data/sample_merchant_summary.pdf` exists and is a valid PDF. A sample is provided in the repo.

---

## Development Workflow

**Iterate quickly:**
```bash
# Terminal 1: Start API (once)
uvicorn ingestion.simulated_api:app --host 127.0.0.1 --port 8000

# Terminal 2: Run pipeline (repeat as needed)
python3 pipeline.py

# Terminal 3: Edit code, run tests
pytest tests/ -v
```

**Monitor changes:**
```bash
# Watch for log output
tail -f logs/ingestion.log

# Check generated data
head data/collated_merchants_with_predictions.csv
```

---

## Configuration

### Model Parameters (edit `config.py`):
- `random_seed` – Reproducibility seed (default: 42)
- `test_size` – Train/test split ratio (default: 0.2 = 80/20)
- `log_level` – Logging verbosity (default: INFO)

### API Settings (edit `config.py`):
- `simulated_api_host` – API hostname (default: localhost)
- `simulated_api_port` – API port (default: 8000)
- `rest_countries_base_url` – Country enrichment API
- `companies_house_base_url` – UK company lookup API

---

## Next Steps

1. **Explore the code:** Check `pipeline.py` for phase overview, then dive into specific modules
2. **Modify features:** Edit `features/feature_builder.py` to add/remove features
3. **Adjust model:** Edit `model/model_trainer.py` to change algorithm or hyperparameters
4. **Extend ingestion:** Add new data sources in `ingestion/orchestrator.py`
5. **Run experiments:** Create branches and test changes without affecting main

---

## Architecture Overview

```
📦 MLE-Hiring/
├── pipeline.py                 # Main orchestration (6 phases)
├── ingestion/
│   ├── orchestrator.py         # Coordinates all data sources
│   ├── collator.py             # Merges data + validates
│   ├── csv_loader.py           # Loads merchants.csv
│   ├── api_client.py           # REST Countries, Companies House
│   ├── pdf_processor.py        # Async PDF extraction
│   ├── web_scraper.py          # Scrapes Claritypay
│   └── simulated_api.py        # Mock API (FastAPI)
├── features/
│   └── feature_builder.py      # Engineers 10 features (no leakage)
├── model/
│   ├── model_trainer.py        # Trains LogisticRegression
│   ├── portfolio.py            # Risk aggregation
│   └── risk_model.pkl          # Saved model
├── reporting/
│   └── llm_reporter.py         # GPT-4 report generation
├── tests/
│   ├── test_pdf_exclusion.py
│   ├── test_feature_builder.py
│   └── ...
├── data/
│   ├── merchants.csv           # 50 merchants
│   ├── collated_merchants.csv  # Merged enriched data
│   └── underwriting_report.txt # Generated insights
└── README.md                   # This file
```

---

## Support & Questions

- **Code issues:** Check `tests/` for examples and expected behavior
- **Data issues:** Verify `data/merchants.csv` format matches `ingestion/validators.py` schema
- **Model questions:** See `features/feature_builder.py` for feature logic
- **API issues:** Review `ingestion/simulated_api.py` for mock data

---

*Last updated: February 15, 2026*
