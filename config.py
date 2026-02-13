"""Configuration management for the merchant underwriting pipeline."""

from pydantic_settings import BaseSettings
from pathlib import Path
import logging


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # API Keys
    openai_api_key: str = ""
    companies_house_api_key: str = ""

    # Simulated API Configuration
    simulated_api_host: str = "localhost"
    simulated_api_port: int = 8000
    simulated_api_base_url: str = "http://localhost:8000"

    # Logging
    log_level: str = "INFO"

    # Model Configuration
    random_seed: int = 42
    test_size: float = 0.2

    # External APIs
    rest_countries_base_url: str = "https://restcountries.com/v3.1"
    companies_house_base_url: str = "https://api.company-information.service.gov.uk"
    claritypay_url: str = "https://claritypay.com"

    class Config:
        env_file = Path(__file__).parent / ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set up logging
        logging.basicConfig(
            level=self.log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


# Global settings instance
settings = Settings()
