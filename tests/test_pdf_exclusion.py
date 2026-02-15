import sys
from pathlib import Path
import csv

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.orchestrator import run_ingestion


def test_pdf_not_in_collated_csv(tmp_path):
    data_dir = Path(__file__).parent.parent / "data"
    # Run ingestion (this will also write data/collated_merchants.csv)
    collated = run_ingestion(data_dir)
    assert collated is not None and len(collated) > 0

    csv_path = Path("data/collated_merchants.csv")
    assert csv_path.exists()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader)

    assert "pdf_summary" not in headers, "pdf_summary should not be present in collated CSV"
