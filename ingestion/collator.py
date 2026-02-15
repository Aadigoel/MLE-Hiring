"""Data collation module to merge data from all sources."""

import logging
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path
from ingestion.validators import MerchantCollated

logger = logging.getLogger(__name__)


class DataCollator:
    """Collate data from multiple sources into unified merchant view."""

    @staticmethod
    def collate(
        merchants_csv: List[Dict],
        api_responses: Dict[str, Dict],
        country_enrichments: Dict[str, Dict],
        company_data: Dict[str, Dict],
        pdf_summaries: Dict[str, str],
        claritypay_info: Optional[Dict],
    ) -> List[Dict]:
        """
        Merge all data sources into unified merchant records.
        
        Args:
            merchants_csv: List of merchants from CSV
            api_responses: Dict mapping merchant_id to API response
            country_enrichments: Dict mapping country_name to country data
            company_data: Dict mapping registration_number to company data
            pdf_summaries: Dict mapping merchant_id to PDF text
            claritypay_info: Scraped Claritypay info
            
        Returns:
            List of collated merchant dicts
        """
        logger.info("Starting data collation from all sources")
        
        collated = []
        
        for merchant in merchants_csv:
            merchant_id = merchant.get("merchant_id")
            country = merchant.get("country")
            reg_number = merchant.get("registration_number")
            
            # Get API response
            api_data = api_responses.get(merchant_id, {})
            
            # Get country enrichment
            country_data = country_enrichments.get(country, {})
            
            # Get company data
            company_info = company_data.get(reg_number, {})
            
            # Get PDF summary
            pdf_text = pdf_summaries.get(merchant_id)
            
            # Check if partner of Claritypay
            is_partner = (
                claritypay_info and
                merchant.get("name") in claritypay_info.get("partners", [])
            )
            
            # Construct collated record
            collated_record = {
                # From CSV
                "merchant_id": merchant_id,
                "name": merchant.get("name"),
                "country": country,
                "registration_number": reg_number,
                "monthly_volume": merchant.get("monthly_volume"),
                "dispute_count": merchant.get("dispute_count"),
                "transaction_count": merchant.get("transaction_count"),
                # From Country API
                "country_code": country_data.get("country_code"),
                "region": country_data.get("region"),
                "subregion": country_data.get("subregion"),
                # From Companies House API
                "company_status": company_info.get("status"),
                "company_incorporation_date": company_info.get("incorporation_date"),
                # From Simulated API
                "last_30d_volume": api_data.get("transaction_summary", {}).get("last_30d_volume"),
                "last_30d_txn_count": api_data.get("transaction_summary", {}).get("last_30d_txn_count"),
                "avg_ticket_size": api_data.get("transaction_summary", {}).get("avg_ticket_size"),
                "internal_risk_flag": api_data.get("internal_risk_flag"),
                "last_review_date": api_data.get("last_review_date"),
                # From PDF
                "pdf_summary": pdf_text[:500] if pdf_text else None,  # First 500 chars
                # From Web Scraping
                "claritypay_partner": is_partner,
            }
            
            try:
                # Validate using Pydantic model
                validated = MerchantCollated(**collated_record)
                collated.append(validated.model_dump())
            except Exception as e:
                logger.warning(f"Failed to validate collated record for {merchant_id}: {e}")
                # Still include record but without validation
                collated.append(collated_record)
        
        logger.info(f"Collated {len(collated)} merchant records")
        return collated

    @staticmethod
    def save_collated_data(collated: List[Dict], output_path: Path) -> None:
        """
        Save collated data to CSV for inspection.
        
        Args:
            collated: List of collated merchant dicts
            output_path: Path to save CSV
        """
        logger.info(f"Saving collated data to {output_path}")
        df = pd.DataFrame(collated)
        df.to_csv(output_path, index=False)
        logger.info(f"Saved {len(collated)} records to {output_path}")
