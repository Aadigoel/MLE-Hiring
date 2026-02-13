"""Web scraping for company information (claritypay.com)."""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


def scrape_claritypay() -> Optional[Dict]:
    """
    Scrape claritypay.com for company information.
    
    Extracts:
    - Main value propositions
    - Partner names
    - Public statistics
    
    Returns:
        Dict with 'propositions', 'partners', 'stats'; None if scraping fails
    """
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("requests or beautifulsoup4 not installed; skipping web scraping")
        return None
    
    try:
        from config import settings
        url = settings.claritypay_url
        
        logger.info(f"Scraping {url}")
        
        # Set a respectful user agent
        headers = {
            "User-Agent": "MLE-Hiring-Pipeline/1.0 (Educational; respectful scraping)"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract propositions (look for common heading patterns)
        propositions = []
        for heading in soup.find_all(["h1", "h2", "h3"]):
            text = heading.get_text(strip=True)
            if text and len(text) > 5 and len(text) < 200:
                propositions.append(text)
        
        # Extract partner names (look for partner/logo sections)
        partners = []
        partner_section = soup.find(["section", "div"], {"class": lambda x: x and "partner" in x.lower()})
        if partner_section:
            for link in partner_section.find_all("a"):
                partner_name = link.get_text(strip=True)
                if partner_name:
                    partners.append(partner_name)
        
        # Extract statistics (look for numbers with units)
        stats = {}
        for text in soup.find_all(string=True):
            text = text.strip()
            if any(keyword in text.lower() for keyword in ["merchant", "transaction", "credit", "issued"]):
                if any(char.isdigit() for char in text):
                    stats[text] = True
        
        logger.info(f"Scraped Claritypay: {len(propositions)} propositions, {len(partners)} partners")
        
        return {
            "propositions": propositions[:5],  # Limit to top 5
            "partners": partners[:10],  # Limit to top 10
            "stats": list(stats.keys())[:5],  # Limit to top 5 stats
        }
        
    except Exception as e:
        logger.warning(f"Failed to scrape claritypay.com: {e}")
        return None
