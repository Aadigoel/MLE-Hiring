"""Integration test script to demonstrate end-to-end ingestion."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion.orchestrator import run_ingestion
from ingestion.logging_setup import get_logger

logger = get_logger(__name__)


def test_ingestion():
    """Test complete ingestion pipeline."""
    logger.info("Starting integration test...")
    
    # Run ingestion
    data_dir = Path(__file__).parent.parent / "data"
    collated = run_ingestion(data_dir)
    
    if collated is None:
        logger.error("Ingestion failed")
        return False
    
    logger.info(f"\n✓ Ingestion successful! Collated {len(collated)} merchants")
    
    # Show sample record
    if collated:
        sample = collated[0]
        logger.info("\nSample collated record:")
        for key, value in list(sample.items())[:10]:
            logger.info(f"  {key}: {value}")
    
    return True


if __name__ == "__main__":
    success = test_ingestion()
    sys.exit(0 if success else 1)
