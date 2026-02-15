"""Tests for data collation."""

import pytest
from ingestion.collator import DataCollator


class TestDataCollator:
    """Test data collation from multiple sources."""

    def test_collate_basic_data(self, sample_merchant_data):
        """Test basic data collation."""
        api_responses = {
            "M001": {
                "merchant_id": "M001",
                "internal_risk_flag": "low",
                "transaction_summary": {
                    "last_30d_volume": 125000.0,
                    "last_30d_txn_count": 3420,
                    "avg_ticket_size": 36.55,
                },
            }
        }
        
        country_enrichments = {
            "United Kingdom": {
                "country_code": "GB",
                "country_name": "United Kingdom",
                "region": "Europe",
                "subregion": None,
            },
            "United States": {
                "country_code": "US",
                "country_name": "United States",
                "region": "Americas",
                "subregion": None,
            },
        }
        
        collated = DataCollator.collate(
            merchants_csv=sample_merchant_data,
            api_responses=api_responses,
            country_enrichments=country_enrichments,
            company_data={},
            pdf_summaries={},
            claritypay_info=None,
        )
        
        assert len(collated) == 2
        assert collated[0]["merchant_id"] == "M001"
        assert collated[0]["country_code"] == "GB"
        assert collated[0]["region"] == "Europe"

    def test_collate_with_company_data(self, sample_merchant_data):
        """Test collation with company data."""
        company_data = {
            "12345678": {
                "company_number": "12345678",
                "company_name": "Test Merchant Ltd",
                "status": "active",
                "incorporation_date": "2020-01-15",
            }
        }
        
        collated = DataCollator.collate(
            merchants_csv=sample_merchant_data,
            api_responses={},
            country_enrichments={},
            company_data=company_data,
            pdf_summaries={},
            claritypay_info=None,
        )
        
        assert len(collated) == 2
        assert collated[0]["company_status"] == "active"

    def test_collate_handles_missing_data(self, sample_merchant_data):
        """Test collation gracefully handles missing data."""
        collated = DataCollator.collate(
            merchants_csv=sample_merchant_data,
            api_responses={},
            country_enrichments={},
            company_data={},
            pdf_summaries={},
            claritypay_info=None,
        )
        
        # Should still collate even with no enrichment data
        assert len(collated) == 2
        assert collated[0]["country_code"] is None
