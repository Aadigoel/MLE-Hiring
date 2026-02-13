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
            DataFrame with engineered features
        """
        logger.info("Engineering features from merchant data")
        
        df = pd.DataFrame(merchants)
        features = pd.DataFrame()
        features["merchant_id"] = df["merchant_id"]
        
        # Dispute rate
        features["dispute_rate"] = df["dispute_count"] / (df["transaction_count"] + 1)
        
        # Volume band (categorical -> ordinal)
        features["volume_band"] = pd.cut(
            df["monthly_volume"],
            bins=[0, 50000, 100000, 200000, np.inf],
            labels=["low", "medium", "high", "very_high"],
        ).cat.codes
        
        # Transaction frequency
        features["avg_transaction_size"] = df["monthly_volume"] / (df["transaction_count"] + 1)
        
        # Geographic risk score (simple proxy based on region)
        features["region_risk"] = df["region"].map(self._get_region_risk).fillna(1.0)
        
        # Company status risk
        features["company_status_risk"] = df["company_status"].map(self._get_company_status_risk).fillna(1.0)
        
        # API-based risk score
        features["api_risk_score"] = df["internal_risk_flag"].map(self._get_risk_score).fillna(1.0)
        
        # Volume velocity (high 30d volume vs monthly volume suggests spike)
        features["volume_velocity"] = (df["last_30d_volume"] / (df["monthly_volume"] + 1)).fillna(1.0)
        
        # Store feature names for model
        self.feature_names = [col for col in features.columns if col != "merchant_id"]
        
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
