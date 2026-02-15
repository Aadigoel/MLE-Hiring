"""Integration tests for the ingestion orchestrator."""

import pytest
from pathlib import Path
from ingestion.orchestrator import IngestionOrchestrator


class TestIngestionOrchestrator:
    """Test end-to-end ingestion orchestration."""

    def test_orchestrator_initialization(self):
        """Test orchestrator can be initialized."""
        orchestrator = IngestionOrchestrator()
        assert orchestrator is not None
        assert orchestrator.merchants_csv == []
        assert orchestrator.api_responses == {}

    def test_csv_loading_in_orchestrator(self, data_dir):
        """Test CSV loading through orchestrator."""
        orchestrator = IngestionOrchestrator()
        csv_path = data_dir / "merchants.csv"
        
        if csv_path.exists():
            success = orchestrator._load_csv(data_dir)
            assert success
            assert len(orchestrator.merchants_csv) > 0

    def test_get_summary(self):
        """Test orchestrator summary generation."""
        orchestrator = IngestionOrchestrator()
        orchestrator.merchants_csv = [{"merchant_id": "M001"}]
        orchestrator.api_responses = {"M001": {}}
        
        summary = orchestrator.get_summary()
        assert summary["merchants_loaded"] == 1
        assert summary["api_responses_fetched"] == 1
