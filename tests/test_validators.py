"""Tests for data validation."""

import pytest
from ingestion.validators import MerchantCSV, SimulatedAPIResponse, TransactionSummary


class TestMerchantCSVValidation:
    """Test merchant CSV schema validation."""

    def test_valid_merchant(self):
        """Test valid merchant data passes validation."""
        data = {
            "merchant_id": "M001",
            "name": "Test Merchant",
            "country": "United Kingdom",
            "registration_number": "12345678",
            "monthly_volume": 100000,
            "dispute_count": 2,
            "transaction_count": 5000,
        }
        merchant = MerchantCSV(**data)
        assert merchant.merchant_id == "M001"

    def test_invalid_merchant_id_format(self):
        """Test merchant ID must start with 'M'."""
        data = {
            "merchant_id": "X001",
            "name": "Test Merchant",
            "country": "United Kingdom",
            "registration_number": "12345678",
            "monthly_volume": 100000,
            "dispute_count": 2,
            "transaction_count": 5000,
        }
        with pytest.raises(ValueError, match="merchant_id must start with"):
            MerchantCSV(**data)

    def test_negative_volume_invalid(self):
        """Test negative volume is rejected."""
        data = {
            "merchant_id": "M001",
            "name": "Test Merchant",
            "country": "United Kingdom",
            "registration_number": "12345678",
            "monthly_volume": -100,
            "dispute_count": 2,
            "transaction_count": 5000,
        }
        with pytest.raises(ValueError):
            MerchantCSV(**data)

    def test_optional_registration_number(self):
        """Test registration number can be None."""
        data = {
            "merchant_id": "M001",
            "name": "Test Merchant",
            "country": "United States",
            "registration_number": None,
            "monthly_volume": 100000,
            "dispute_count": 2,
            "transaction_count": 5000,
        }
        merchant = MerchantCSV(**data)
        assert merchant.registration_number is None


class TestSimulatedAPIResponseValidation:
    """Test simulated API response validation."""

    def test_valid_api_response(self):
        """Test valid API response passes validation."""
        data = {
            "merchant_id": "M001",
            "internal_risk_flag": "low",
            "transaction_summary": {
                "last_30d_volume": 125000.0,
                "last_30d_txn_count": 3420,
                "avg_ticket_size": 36.55,
            },
        }
        response = SimulatedAPIResponse(**data)
        assert response.merchant_id == "M001"
        assert response.internal_risk_flag == "low"

    def test_invalid_risk_flag(self):
        """Test invalid risk flag is rejected."""
        data = {
            "merchant_id": "M001",
            "internal_risk_flag": "critical",
            "transaction_summary": {
                "last_30d_volume": 125000.0,
                "last_30d_txn_count": 3420,
                "avg_ticket_size": 36.55,
            },
        }
        with pytest.raises(ValueError):
            SimulatedAPIResponse(**data)

    def test_negative_volume_invalid(self):
        """Test negative transaction volume is rejected."""
        data = {
            "merchant_id": "M001",
            "internal_risk_flag": "low",
            "transaction_summary": {
                "last_30d_volume": -1000.0,
                "last_30d_txn_count": 3420,
                "avg_ticket_size": 36.55,
            },
        }
        with pytest.raises(ValueError):
            SimulatedAPIResponse(**data)
