"""Tests for CSV loading."""

import pytest
from pathlib import Path
from ingestion.csv_loader import load_merchants_csv


class TestCSVLoader:
    """Test merchant CSV loading and validation."""

    def test_load_valid_csv(self, data_dir):
        """Test loading valid merchants CSV."""
        csv_path = data_dir / "merchants.csv"
        if csv_path.exists():
            merchants, errors = load_merchants_csv(csv_path)
            assert len(merchants) > 0
            assert len(errors) == 0
            assert merchants[0]["merchant_id"].startswith("M")

    def test_nonexistent_csv_raises_error(self):
        """Test loading non-existent CSV raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_merchants_csv(Path("nonexistent.csv"))

    def test_csv_with_valid_and_invalid_rows(self, tmp_path):
        """Test handling of mixed valid/invalid rows."""
        csv_content = """merchant_id,name,country,registration_number,monthly_volume,dispute_count,transaction_count
M001,Valid Merchant,United Kingdom,N001234567,100000,2,5000
INVALID,Invalid ID,United Kingdom,N001234568,-100,2,5000
M002,Another Valid,United States,,50000,1,2000
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        merchants, errors = load_merchants_csv(csv_file)
        # Should have 2 valid merchants
        assert len(merchants) == 2
        assert len(errors) >= 1  # At least one error from invalid merchant
