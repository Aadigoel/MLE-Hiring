"""Tests for feature engineering."""

import pytest
import pandas as pd
from features.feature_builder import FeatureBuilder


class TestFeatureBuilder:
    """Test feature engineering."""

    def test_build_features(self, sample_collated_data):
        """Test feature building from merchant data."""
        builder = FeatureBuilder()
        features = builder.build_features(sample_collated_data)
        
        assert len(features) == len(sample_collated_data)
        # Verify key features present (new feature set without leakage)
        assert "log_monthly_volume" in features.columns
        assert "log_transaction_count" in features.columns
        assert "volume_band" in features.columns
        assert len(builder.feature_names) > 0
        assert "dispute_rate" not in features.columns  # Prevent leakage!

    def test_dispute_rate_calculation(self, sample_collated_data):
        """Test that dispute rate is NOT in features (prevents data leakage)."""
        builder = FeatureBuilder()
        features = builder.build_features(sample_collated_data)
        
        # Verify dispute-based features are excluded to prevent leakage
        assert "dispute_rate" not in features.columns
        assert "dispute_count" not in features.columns
        
        # But legitimate volume-based features should be present
        assert "log_monthly_volume" in features.columns
        assert "log_transaction_count" in features.columns

    def test_volume_band_categorization(self, sample_collated_data):
        """Test volume band categorization."""
        builder = FeatureBuilder()
        features = builder.build_features(sample_collated_data)
        
        # Volume bands should be ordinal (0, 1, 2, 3)
        assert features["volume_band"].min() >= 0
        assert features["volume_band"].max() <= 3

    def test_region_risk_scoring(self):
        """Test region risk scoring."""
        test_regions = ["Europe", "Americas", "Asia", "Africa", "Oceania"]
        scores = [FeatureBuilder._get_region_risk(r) for r in test_regions]
        
        # All scores should be between 0 and 1
        assert all(0 <= s <= 1 for s in scores)
        # Europe should have lower risk than Africa
        assert FeatureBuilder._get_region_risk("Europe") < FeatureBuilder._get_region_risk("Africa")

    def test_company_status_risk_scoring(self):
        """Test company status risk scoring."""
        test_statuses = ["active", "restricted", "dissolved"]
        scores = [FeatureBuilder._get_company_status_risk(s) for s in test_statuses]
        
        # All scores should be between 0 and 1
        assert all(0 <= s <= 1 for s in scores)
        # Active should have lowest risk
        assert FeatureBuilder._get_company_status_risk("active") < FeatureBuilder._get_company_status_risk("dissolved")

    def test_risk_score_conversion(self):
        """Test risk flag to risk score conversion."""
        assert FeatureBuilder._get_risk_score("low") < FeatureBuilder._get_risk_score("medium")
        assert FeatureBuilder._get_risk_score("medium") < FeatureBuilder._get_risk_score("high")
