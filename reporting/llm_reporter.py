"""LLM-powered report generation."""

import logging
from typing import Dict, Optional
import json

logger = logging.getLogger(__name__)


class LLMReporter:
    """Generate underwriting reports using LLM."""

    def __init__(self, api_key: str = "", model: str = "gpt-4"):
        """
        Initialize LLM reporter.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4)
        """
        self.api_key = api_key
        self.model = model
        self.client = None
        
        if api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
            except ImportError:
                logger.warning("OpenAI package not installed; report generation will be limited")

    def generate_report(
        self,
        merchants: list,
        portfolio_metrics: Dict,
        model_predictions: Dict,
    ) -> Optional[str]:
        """
        Generate underwriting report using LLM.
        
        Args:
            merchants: List of merchant dicts with collated data
            portfolio_metrics: Portfolio-level risk metrics
            model_predictions: Model predictions for each merchant
            
        Returns:
            Generated report text; None if LLM not available
        """
        if not self.client:
            logger.warning("LLM client not initialized; generating template report")
            return self._generate_template_report(merchants, portfolio_metrics)
        
        logger.info("Generating underwriting report via LLM")
        
        # Prepare context for LLM
        context = self._prepare_context(merchants, portfolio_metrics, model_predictions)
        
        # LLM prompt
        system_prompt = """You are an expert BNPL underwriting analyst. 
Generate a concise (1-2 page) underwriting report for the risk team summarizing:
1. Portfolio overview and key metrics
2. Merchant risk profile by risk band
3. Key risk factors and red flags
4. Recommended actions
Be precise, actionable, and professional."""
        
        user_prompt = f"""Generate an underwriting report based on this data:

{json.dumps(context, indent=2)}

Focus on:
- Key risk factors driving high-risk classifications
- Geographic and sector trends
- Portfolio diversification
- Recommended underwriting actions"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            
            report = response.content[0].text
            logger.info("Report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"LLM report generation failed: {e}")
            return self._generate_template_report(merchants, portfolio_metrics)

    @staticmethod
    def _prepare_context(merchants: list, portfolio_metrics: Dict, model_predictions: Dict) -> Dict:
        """Prepare merchant and portfolio data for LLM."""
        return {
            "portfolio_summary": {
                "total_merchants": portfolio_metrics["total_merchants"],
                "high_risk_count": portfolio_metrics["high_risk_count"],
                "high_risk_percentage": portfolio_metrics["high_risk_percentage"],
                "avg_risk_probability": portfolio_metrics["avg_risk_probability"],
                "risk_distribution": portfolio_metrics["risk_distribution"],
            },
            "top_risk_merchants": [
                {
                    "merchant_id": m["merchant_id"],
                    "name": m.get("name", "Unknown"),
                    "country": m.get("country", "Unknown"),
                    "monthly_volume": m.get("monthly_volume"),
                    "dispute_rate": (m.get("dispute_count", 0) / (m.get("transaction_count", 1) + 1)),
                }
                for m in merchants[:10]
            ],
        }

    @staticmethod
    def _generate_template_report(merchants: list, portfolio_metrics: Dict) -> str:
        """Generate a basic template report when LLM is not available."""
        report = f"""MERCHANT UNDERWRITING REPORT
Generated: Report generated from pipeline data.

PORTFOLIO SUMMARY
- Total Merchants: {portfolio_metrics['total_merchants']}
- High-Risk Merchants: {portfolio_metrics['high_risk_count']} ({portfolio_metrics['high_risk_percentage']:.1f}%)
- Average Risk Probability: {portfolio_metrics['avg_risk_probability']:.3f}
- Risk Distribution: {portfolio_metrics['risk_distribution']}

KEY METRICS
- Total Portfolio Volume: {portfolio_metrics.get('total_volume', 'N/A')}
- Expected Loss: {portfolio_metrics['expected_loss']:.2f}

TOP RISK FACTORS
1. Merchant concentration in high-risk geographies
2. Elevated dispute rates in specific sectors
3. Volume volatility patterns

RECOMMENDATIONS
1. Increase monitoring frequency for high-risk merchants
2. Implement stricter onboarding criteria
3. Consider portfolio rebalancing

This is a template report. For detailed analysis, configure OpenAI API access.
"""
        return report
