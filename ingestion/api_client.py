"""API clients for external data sources (REST Countries, Companies House)."""

import logging
import requests
from typing import Optional, Dict
from config import settings

logger = logging.getLogger(__name__)


class RestCountriesClient:
    """Client for REST Countries API (no authentication required)."""

    def __init__(self, base_url: str = settings.rest_countries_base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "MLE-Hiring-Pipeline/1.0"
        })

    def get_country_by_name(self, country_name: str) -> Optional[Dict]:
        """
        Fetch country data by name.
        
        Args:
            country_name: Name of the country
            
        Returns:
            Country data dict with code, name, region, subregion; None if not found
        """
        try:
            url = f"{self.base_url}/name/{country_name}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                country = data[0]
                return {
                    "country_code": country.get("cca2"),
                    "country_name": country.get("name", {}).get("official", country_name),
                    "region": country.get("region"),
                    "subregion": country.get("subregion"),
                }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch country data for {country_name}: {e}")
        
        return None

    def get_country_by_code(self, country_code: str) -> Optional[Dict]:
        """
        Fetch country data by alpha-2 or alpha-3 code.
        
        Args:
            country_code: ISO country code (2 or 3 letters)
            
        Returns:
            Country data dict; None if not found
        """
        try:
            url = f"{self.base_url}/alpha/{country_code}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            country = response.json()
            return {
                "country_code": country.get("cca2"),
                "country_name": country.get("name", {}).get("official", country_code),
                "region": country.get("region"),
                "subregion": country.get("subregion"),
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch country data for {country_code}: {e}")
        
        return None


class CompaniesHouseClient:
    """Client for Companies House API (UK company information)."""

    def __init__(self, api_key: str = settings.companies_house_api_key, 
                 base_url: str = settings.companies_house_base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        if api_key:
            self.session.auth = (api_key, "")
        self.session.headers.update({
            "User-Agent": "MLE-Hiring-Pipeline/1.0"
        })

    def get_company(self, company_number: str) -> Optional[Dict]:
        """
        Fetch company data by company number.
        
        Args:
            company_number: UK Companies House registration number
            
        Returns:
            Company data dict with name, status, incorporation_date; None if not found
        """
        if not self.api_key:
            logger.warning("Companies House API key not configured; skipping company lookup")
            return None
        
        try:
            url = f"{self.base_url}/company/{company_number}"
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            company = response.json()
            return {
                "company_number": company.get("company_number"),
                "company_name": company.get("company_name"),
                "status": company.get("company_status"),
                "incorporation_date": company.get("date_of_creation"),
            }
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch company data for {company_number}: {e}")
        
        return None
