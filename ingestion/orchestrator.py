"""Main ingestion orchestrator for the merchant underwriting pipeline."""

import asyncio
import logging
from pathlib import Path
from typing import Tuple, List, Dict, Optional

from ingestion.logging_setup import get_logger
from ingestion.csv_loader import load_merchants_csv
from ingestion.api_client import RestCountriesClient, CompaniesHouseClient
from ingestion.pdf_processor import process_pdf_async
from ingestion.web_scraper import scrape_claritypay
from ingestion.simulated_api import MOCK_MERCHANTS
from ingestion.collator import DataCollator
from config import settings

logger = get_logger(__name__)


class IngestionOrchestrator:
    """
    Orchestrate all ingestion operations from multiple sources.
    
    Handles:
    1. CSV loading and validation
    2. API calls (REST Countries, Companies House, Simulated API)
    3. PDF processing (async)
    4. Web scraping
    5. Data collation from all sources
    """

    def __init__(self):
        """Initialize ingestion orchestrator."""
        self.countries_client = RestCountriesClient()
        self.companies_client = CompaniesHouseClient()
        
        self.merchants_csv = []
        self.api_responses = {}
        self.country_enrichments = {}
        self.company_data = {}
        self.pdf_summaries = {}
        self.claritypay_info = None

    def ingest(self, data_dir: Path) -> Optional[List[Dict]]:
        """
        Run complete ingestion pipeline.
        
        Args:
            data_dir: Path to data directory
            
        Returns:
            List of collated merchant records; None if critical step fails
        """
        logger.info("=" * 80)
        logger.info("STARTING INGESTION PIPELINE")
        logger.info("=" * 80)
        
        # Phase 1: Load CSV
        logger.info("PHASE 1: Loading merchant CSV...")
        if not self._load_csv(data_dir):
            logger.error("Failed to load CSV; aborting pipeline")
            return None
        
        # Phase 2: Fetch API data (REST Countries, Companies House, Simulated API)
        logger.info("PHASE 2: Fetching data from external APIs...")
        self._fetch_api_data()
        
        # Phase 3: Process PDF (async)
        logger.info("PHASE 3: Processing PDF asynchronously...")
        asyncio.run(self._process_pdf(data_dir))
        
        # Phase 4: Scrape web data
        logger.info("PHASE 4: Scraping Claritypay website...")
        self._scrape_web_data()
        
        # Phase 5: Collate all data
        logger.info("PHASE 5: Collating data from all sources...")
        collated = self._collate_data()
        
        logger.info("=" * 80)
        logger.info("INGESTION PIPELINE COMPLETE")
        logger.info("=" * 80)
        
        return collated

    def _load_csv(self, data_dir: Path) -> bool:
        """Load and validate CSV data."""
        csv_path = data_dir / "merchants.csv"
        
        if not csv_path.exists():
            logger.error(f"CSV file not found: {csv_path}")
            return False
        
        try:
            self.merchants_csv, errors = load_merchants_csv(csv_path)
            logger.info(f"✓ Loaded {len(self.merchants_csv)} merchants from CSV")
            
            if errors:
                logger.warning(f"⚠ {len(errors)} validation errors:")
                for error in errors[:5]:  # Show first 5
                    logger.warning(f"  - {error}")
                if len(errors) > 5:
                    logger.warning(f"  ... and {len(errors) - 5} more")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return False

    def _fetch_api_data(self) -> None:
        """Fetch data from all external APIs."""
        # Fetch simulated API data for all merchants
        logger.info("Calling Simulated Risk API...")
        for merchant in self.merchants_csv:
            merchant_id = merchant.get("merchant_id")
            
            # In real scenario, would call HTTP endpoint
            # For now, use mock data
            if merchant_id in MOCK_MERCHANTS:
                self.api_responses[merchant_id] = MOCK_MERCHANTS[merchant_id]
                logger.debug(f"✓ Fetched API data for {merchant_id}")
            else:
                logger.warning(f"⚠ No API data for {merchant_id}")
        
        logger.info(f"✓ Fetched API data for {len(self.api_responses)} merchants")
        
        # Enrich with country data (REST Countries)
        logger.info("Enriching with country data from REST Countries API...")
        unique_countries = set(m.get("country") for m in self.merchants_csv)
        
        for country in unique_countries:
            if country:
                enrichment = self.countries_client.get_country_by_name(country)
                if enrichment:
                    self.country_enrichments[country] = enrichment
                    logger.debug(f"✓ Enriched {country}: {enrichment.get('country_code')}")
                else:
                    logger.warning(f"⚠ Could not enrich {country}")
        
        logger.info(f"✓ Enriched {len(self.country_enrichments)} countries")
        
        # Fetch company data (Companies House)
        if settings.companies_house_api_key:
            logger.info("Fetching UK company data from Companies House API...")
            for merchant in self.merchants_csv:
                reg_number = merchant.get("registration_number")
                country = merchant.get("country")
                
                if reg_number and country == "United Kingdom":
                    company_info = self.companies_client.get_company(reg_number)
                    if company_info:
                        self.company_data[reg_number] = company_info
                        logger.debug(f"✓ Fetched company {reg_number}")
                    else:
                        logger.warning(f"⚠ Could not fetch company {reg_number}")
            
            logger.info(f"✓ Fetched data for {len(self.company_data)} UK companies")
        else:
            logger.info("⊙ Companies House API key not configured; skipping UK company lookup")

    async def _process_pdf(self, data_dir: Path) -> None:
        """Process PDF files asynchronously."""
        pdf_path = data_dir / "sample_merchant_summary.pdf"
        
        if not pdf_path.exists():
            logger.warning(f"PDF file not found: {pdf_path}")
            return
        
        try:
            # Process PDF
            pdf_text = await process_pdf_async(pdf_path)
            
            if pdf_text:
                # In production, would map PDF to specific merchants
                # For now, associate with first merchant for demo
                if self.merchants_csv:
                    merchant_id = self.merchants_csv[0].get("merchant_id")
                    self.pdf_summaries[merchant_id] = pdf_text
                    logger.info(f"✓ Processed PDF ({len(pdf_text)} chars)")
            else:
                logger.warning("⚠ PDF processing returned no text")
                
        except Exception as e:
            logger.error(f"Failed to process PDF: {e}")

    def _scrape_web_data(self) -> None:
        """Scrape web data from company website."""
        try:
            self.claritypay_info = scrape_claritypay()
            
            if self.claritypay_info:
                logger.info(
                    f"✓ Scraped Claritypay: {len(self.claritypay_info.get('propositions', []))} "
                    f"propositions, {len(self.claritypay_info.get('partners', []))} partners"
                )
            else:
                logger.warning("⚠ Web scraping returned no data")
                
        except Exception as e:
            logger.error(f"Failed to scrape web data: {e}")

    def _collate_data(self) -> Optional[List[Dict]]:
        """Collate all ingested data into unified merchant records."""
        try:
            collated = DataCollator.collate(
                merchants_csv=self.merchants_csv,
                api_responses=self.api_responses,
                country_enrichments=self.country_enrichments,
                company_data=self.company_data,
                pdf_summaries=self.pdf_summaries,
                claritypay_info=self.claritypay_info,
            )
            
            logger.info(f"✓ Collated {len(collated)} merchant records")
            
            # Save collated data to CSV for inspection
            output_path = Path("data/collated_merchants.csv")
            DataCollator.save_collated_data(collated, output_path)
            logger.info(f"✓ Saved collated data to {output_path}")
            
            return collated
            
        except Exception as e:
            logger.error(f"Failed to collate data: {e}")
            return None

    def get_summary(self) -> Dict:
        """Get summary of ingestion results."""
        return {
            "merchants_loaded": len(self.merchants_csv),
            "api_responses_fetched": len(self.api_responses),
            "countries_enriched": len(self.country_enrichments),
            "companies_fetched": len(self.company_data),
            "pdfs_processed": len(self.pdf_summaries),
            "web_data_scraped": bool(self.claritypay_info),
        }


def run_ingestion(data_dir: Optional[Path] = None) -> Optional[List[Dict]]:
    """
    Convenience function to run complete ingestion pipeline.
    
    Args:
        data_dir: Path to data directory (default: ./data)
        
    Returns:
        List of collated merchant records
    """
    if data_dir is None:
        data_dir = Path("data")
    
    orchestrator = IngestionOrchestrator()
    collated = orchestrator.ingest(data_dir)
    
    # Print summary
    summary = orchestrator.get_summary()
    logger.info("\nINGESTION SUMMARY:")
    for key, value in summary.items():
        logger.info(f"  {key}: {value}")
    
    return collated
