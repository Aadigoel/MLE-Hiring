"""Simulated internal API for merchant risk and transaction data."""

from fastapi import FastAPI, HTTPException
from typing import Dict
import logging
from datetime import date, timedelta
import random

from ingestion.validators import SimulatedAPIResponse, TransactionSummary

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simulated Merchant Risk API",
    description="Mock internal API returning merchant risk flags and transaction summaries",
    version="1.0.0",
)

# Mock data store (in production, this would be a database)
MOCK_MERCHANTS = {
    "M001": {
        "merchant_id": "M001",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 125000.00,
            "last_30d_txn_count": 3420,
            "avg_ticket_size": 36.55,
        },
        "last_review_date": "2024-01-15",
    },
    "M002": {
        "merchant_id": "M002",
        "internal_risk_flag": "high",
        "transaction_summary": {
            "last_30d_volume": 89000.00,
            "last_30d_txn_count": 2100,
            "avg_ticket_size": 42.38,
        },
        "last_review_date": "2024-02-01",
    },
    "M003": {
        "merchant_id": "M003",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 210000.00,
            "last_30d_txn_count": 5800,
            "avg_ticket_size": 36.21,
        },
        "last_review_date": "2024-01-20",
    },
    "M004": {
        "merchant_id": "M004",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 78000.00,
            "last_30d_txn_count": 1890,
            "avg_ticket_size": 41.27,
        },
        "last_review_date": "2024-02-05",
    },
    "M005": {
        "merchant_id": "M005",
        "internal_risk_flag": "medium",
        "transaction_summary": {
            "last_30d_volume": 45000.00,
            "last_30d_txn_count": 1200,
            "avg_ticket_size": 37.50,
        },
        "last_review_date": "2024-01-25",
    },
    "M006": {
        "merchant_id": "M006",
        "internal_risk_flag": "medium",
        "transaction_summary": {
            "last_30d_volume": 320000.00,
            "last_30d_txn_count": 8900,
            "avg_ticket_size": 35.96,
        },
        "last_review_date": "2024-02-08",
    },
    "M007": {
        "merchant_id": "M007",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 156000.00,
            "last_30d_txn_count": 4100,
            "avg_ticket_size": 38.05,
        },
        "last_review_date": "2024-01-30",
    },
    "M008": {
        "merchant_id": "M008",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 67000.00,
            "last_30d_txn_count": 2100,
            "avg_ticket_size": 31.90,
        },
        "last_review_date": "2024-02-10",
    },
    "M009": {
        "merchant_id": "M009",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 34000.00,
            "last_30d_txn_count": 980,
            "avg_ticket_size": 34.69,
        },
        "last_review_date": "2024-02-03",
    },
}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/merchant/{merchant_id}", response_model=SimulatedAPIResponse)
def get_merchant_risk(merchant_id: str):
    """
    Get merchant risk data and transaction summary.
    
    Args:
        merchant_id: The merchant ID (e.g., M001)
        
    Returns:
        SimulatedAPIResponse with risk flag and transaction summary
        
    Raises:
        HTTPException: If merchant not found
    """
    if merchant_id not in MOCK_MERCHANTS:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    logger.info(f"Retrieving risk data for merchant {merchant_id}")
    return MOCK_MERCHANTS[merchant_id]


@app.post("/merchant/{merchant_id}")
def update_merchant_risk(merchant_id: str, data: Dict):
    """
    Update merchant risk data (for testing purposes).
    
    Args:
        merchant_id: The merchant ID
        data: Risk data to update
        
    Returns:
        Updated merchant data
    """
    if merchant_id not in MOCK_MERCHANTS:
        raise HTTPException(status_code=404, detail="Merchant not found")
    
    logger.info(f"Updating risk data for merchant {merchant_id}")
    MOCK_MERCHANTS[merchant_id].update(data)
    return MOCK_MERCHANTS[merchant_id]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
