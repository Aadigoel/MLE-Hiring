"""Portfolio-level risk aggregation."""

import logging
import pandas as pd
from typing import Dict

logger = logging.getLogger(__name__)


class PortfolioRiskAggregator:
    """Aggregate individual merchant risks to portfolio level."""

    @staticmethod
    def aggregate(
        merchants_with_predictions: pd.DataFrame,
        risk_threshold: float = 0.5,
    ) -> Dict:
        """
        Aggregate merchant risks to portfolio metrics.
        
        Args:
            merchants_with_predictions: DataFrame with merchant_id and risk_probability
            risk_threshold: Threshold to classify as high-risk (default 0.5)
            
        Returns:
            Dict with portfolio metrics
        """
        logger.info("Aggregating portfolio-level risk metrics")
        
        # Classify as high-risk
        merchants_with_predictions["is_high_risk"] = (
            merchants_with_predictions["risk_probability"] >= risk_threshold
        ).astype(int)
        
        # Calculate metrics
        total_merchants = len(merchants_with_predictions)
        high_risk_count = merchants_with_predictions["is_high_risk"].sum()
        high_risk_pct = 100 * high_risk_count / total_merchants
        
        # Expected loss (sum of risk probabilities weighted by volume)
        if "monthly_volume" in merchants_with_predictions.columns:
            merchants_with_predictions["risk_weighted_volume"] = (
                merchants_with_predictions["risk_probability"]
                * merchants_with_predictions["monthly_volume"]
            )
            expected_loss = merchants_with_predictions["risk_weighted_volume"].sum()
            total_volume = merchants_with_predictions["monthly_volume"].sum()
        else:
            expected_loss = merchants_with_predictions["risk_probability"].sum()
            total_volume = None
        
        # Risk distribution
        risk_bands = {
            "low": (
                merchants_with_predictions["risk_probability"] < 0.33
            ).sum(),
            "medium": (
                (merchants_with_predictions["risk_probability"] >= 0.33)
                & (merchants_with_predictions["risk_probability"] < 0.66)
            ).sum(),
            "high": (
                merchants_with_predictions["risk_probability"] >= 0.66
            ).sum(),
        }
        
        metrics = {
            "total_merchants": total_merchants,
            "high_risk_count": high_risk_count,
            "high_risk_percentage": high_risk_pct,
            "expected_loss": expected_loss,
            "total_volume": total_volume,
            "risk_distribution": risk_bands,
            "avg_risk_probability": merchants_with_predictions["risk_probability"].mean(),
        }
        
        logger.info(f"Portfolio metrics: {high_risk_count}/{total_merchants} high-risk merchants")
        logger.info(f"Expected loss: {expected_loss:.2f}, Risk distribution: {risk_bands}")
        
        return metrics
