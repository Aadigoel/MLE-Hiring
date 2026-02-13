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
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(
            "merchant_id,name,country,registration_number,monthly_volume,dispute_count,transaction_count\n"
            "M001,Valid Merchant,UK,12345678,100000,2,5000\n"
            "INVALID,Invalid ID,UK,12345678,-100,2,5000\n"
            "M002,Another Valid,US,,50000,1,2000\n"
        )
        
        merchants, errors = load_merchants_csv(csv_file)
        assert len(merchants) == 2  # Only valid rows
        assert len(errors) == 1  # One error
