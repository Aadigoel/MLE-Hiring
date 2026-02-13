"""CSV data loading with validation."""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Tuple
from .validators import MerchantCSV

logger = logging.getLogger(__name__)


def load_merchants_csv(csv_path: Path) -> Tuple[List[dict], List[str]]:
    """
    Load and validate merchants from CSV.
    
    Args:
        csv_path: Path to merchants.csv
        
    Returns:
        Tuple of (valid_merchants, validation_errors)
        
    Raises:
        FileNotFoundError: If CSV file does not exist
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    logger.info(f"Loading merchants from {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        raise
    
    valid_merchants = []
    validation_errors = []
    
    for idx, row in df.iterrows():
        try:
            merchant_dict = row.to_dict()
            # Handle NaN values
            merchant_dict = {k: v if pd.notna(v) else None for k, v in merchant_dict.items()}
            
            # Validate using Pydantic model
            merchant = MerchantCSV(**merchant_dict)
            valid_merchants.append(merchant.model_dump())
            
        except Exception as e:
            error_msg = f"Row {idx}: {str(e)}"
            logger.warning(f"Validation error: {error_msg}")
            validation_errors.append(error_msg)
    
    logger.info(f"Loaded {len(valid_merchants)} valid merchants, {len(validation_errors)} errors")
    
    return valid_merchants, validation_errors
