"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def data_dir():
    """Return the data directory path."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_merchant_data():
    """Return sample merchant data for testing."""
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
