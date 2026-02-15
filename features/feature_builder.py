"""Feature engineering for risk model."""

import logging
import pandas as pd
from typing import List, Dict
import numpy as np

logger = logging.getLogger(__name__)


class FeatureBuilder:
    """Build features from collated merchant data for risk modeling."""

    def __init__(self):
        """Initialize feature builder."""
        self.feature_names = []

    def build_features(self, merchants: List[Dict]) -> pd.DataFrame:
        """
        Engineer features from collated merchant data.
        
        Args:
            merchants: List of collated merchant dictionaries
            
        Returns:
            DataFrame with engineered features (numeric only, excluding merchant_id)
            
        Note:
            Intentionally excludes dispute_count to prevent data leakage when
            predicting high_dispute_risk (which is defined using dispute_count).
        """
        logger.info("Engineering features from merchant data")
        
        df = pd.DataFrame(merchants)
        features = pd.DataFrame()
        
        # Volume-based features (legitimate predictors)
        features["log_monthly_volume"] = np.log1p(df["monthly_volume"])
        features["log_transaction_count"] = np.log1p(df["transaction_count"])
        
        # Ticket size and volatility
        features["avg_transaction_size"] = df["monthly_volume"] / (df["transaction_count"] + 1)
        features["volume_transaction_ratio"] = df["monthly_volume"] / (df["transaction_count"] + 1)
        
        # Volume band (categorical -> ordinal)
        features["volume_band"] = pd.cut(
            df["monthly_volume"],
            bins=[0, 50000, 100000, 200000, np.inf],
            labels=["low", "medium", "high", "very_high"],
        ).cat.codes
        
        # Geographic risk score (from enriched data)
        features["region_risk"] = df["region"].map(self._get_region_risk).fillna(1.0)
        
        # Company status risk (from Companies House)
        features["company_status_risk"] = df["company_status"].map(self._get_company_status_risk).fillna(1.0)
        
        # API-based risk score (internal assessment)
        features["api_risk_score"] = df["internal_risk_flag"].map(self._get_risk_score).fillna(1.0)
        
        # Enrichment flags (indicates data availability/quality)
        features["has_country_data"] = df["country_code"].notna().astype(int)
        features["has_company_data"] = df["company_status"].notna().astype(int)
        features["is_uk_registered"] = (df["country"] == "United Kingdom").astype(int)
        
        # Store feature names for model
        self.feature_names = [col for col in features.columns]
        
        logger.info(f"Engineered {len(self.feature_names)} features: {self.feature_names}")
        
        return features

    @staticmethod
    def _get_region_risk(region: str) -> float:
        """
        Get risk score for a geographic region.
        
        Args:
            region: Region name
            
        Returns:
            Risk score (0-1, lower is better)
        """
        # This is a simplification; in production, use actual underwriting data
        risk_map = {
            "Europe": 0.3,
            "Americas": 0.4,
            "Asia": 0.5,
            "Africa": 0.6,
            "Oceania": 0.35,
        }
        return risk_map.get(region, 1.0)

    @staticmethod
    def _get_company_status_risk(status: str) -> float:
        """
        Get risk score for company status.
        
        Args:
            status: Company status
            
        Returns:
            Risk score (0-1, lower is better)
        """
        risk_map = {
            "active": 0.2,
            "restricted": 0.7,
            "dissolved": 1.0,
            "liquidation": 1.0,
            "administration": 0.8,
        }
        return risk_map.get(status, 1.0)

    @staticmethod
    def _get_risk_score(risk_flag: str) -> float:
        """
        Convert internal risk flag to numeric score.
        
        Args:
            risk_flag: Risk flag (low, medium, high)
            
        Returns:
            Risk score (0-1)
        """
        risk_map = {"low": 0.2, "medium": 0.5, "high": 0.8}
        return risk_map.get(risk_flag, 1.0)
