"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def data_dir():
    """Return the data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_merchant_data():
    """Return sample merchant data for testing (basic CSV data)."""
    return [
        {
            "merchant_id": "M001",
            "name": "Test Merchant 1",
            "country": "United Kingdom",
            "registration_number": "12345678",
            "monthly_volume": 100000,
            "dispute_count": 2,
            "transaction_count": 5000,
        },
        {
            "merchant_id": "M002",
            "name": "Test Merchant 2",
            "country": "United States",
            "registration_number": None,
            "monthly_volume": 50000,
            "dispute_count": 1,
            "transaction_count": 2000,
        },
    ]


@pytest.fixture
def sample_collated_data():
    """Return fully collated merchant data for testing."""
    return [
        {
            "merchant_id": "M001",
            "name": "Test Merchant 1",
            "country": "United Kingdom",
            "country_code": "GB",
            "region": "Europe",
            "subregion": None,
            "registration_number": "12345678",
            "company_status": "active",
            "company_incorporation_date": None,
            "monthly_volume": 100000,
            "dispute_count": 2,
            "transaction_count": 5000,
            "last_30d_volume": 125000,
            "last_30d_txn_count": 3420,
            "avg_ticket_size": 36.55,
            "internal_risk_flag": "low",
            "last_review_date": None,
            "pdf_summary": None,
            "claritypay_partner": False,
        },
        {
            "merchant_id": "M002",
            "name": "Test Merchant 2",
            "country": "United States",
            "country_code": "US",
            "region": "Americas",
            "subregion": None,
            "registration_number": None,
            "company_status": None,
            "company_incorporation_date": None,
            "monthly_volume": 50000,
            "dispute_count": 1,
            "transaction_count": 2000,
            "last_30d_volume": 89000,
            "last_30d_txn_count": 2100,
            "avg_ticket_size": 42.38,
            "internal_risk_flag": "medium",
            "last_review_date": None,
            "pdf_summary": None,
            "claritypay_partner": False,
        },
    ]

