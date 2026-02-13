"""Pydantic models for data validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date


class TransactionSummary(BaseModel):
    """Transaction summary data from simulated API."""

    last_30d_volume: float = Field(..., ge=0)
    last_30d_txn_count: int = Field(..., ge=0)
    avg_ticket_size: float = Field(..., ge=0)


class SimulatedAPIResponse(BaseModel):
    """Response schema from the simulated internal API."""

    merchant_id: str
    internal_risk_flag: str = Field(..., pattern="^(low|medium|high)$")
    transaction_summary: TransactionSummary
    last_review_date: Optional[date] = None


class MerchantCSV(BaseModel):
    """Schema for merchants.csv input."""

    merchant_id: str
    name: str
    country: str
    registration_number: Optional[str] = None
    monthly_volume: float = Field(..., ge=0)
    dispute_count: int = Field(..., ge=0)
    transaction_count: int = Field(..., ge=0)

    @validator("merchant_id")
    def validate_merchant_id(cls, v):
        if not v.startswith("M"):
            raise ValueError("merchant_id must start with 'M'")
        return v


class CountryData(BaseModel):
    """Country data enrichment from REST Countries API."""

    country_code: str
    country_name: str
    region: Optional[str] = None
    subregion: Optional[str] = None


class CompanyInfo(BaseModel):
    """Company information from Companies House API."""

    company_number: str
    company_name: str
    status: str
    incorporation_date: Optional[date] = None


class MerchantCollated(BaseModel):
    """Fully collated merchant data from all sources."""

    merchant_id: str
    name: str
    country: str
    country_code: Optional[str] = None
    region: Optional[str] = None
    subregion: Optional[str] = None
    registration_number: Optional[str] = None
    company_status: Optional[str] = None
    company_incorporation_date: Optional[date] = None
    monthly_volume: float
    dispute_count: int
    transaction_count: int
    last_30d_volume: Optional[float] = None
    last_30d_txn_count: Optional[int] = None
    avg_ticket_size: Optional[float] = None
    internal_risk_flag: Optional[str] = None
    pdf_summary: Optional[str] = None
    last_review_date: Optional[date] = None
    claritypay_partner: Optional[bool] = None
