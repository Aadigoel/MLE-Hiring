"""Main pipeline orchestration script for the merchant underwriting pipeline."""

import logging
from pathlib import Path
import pandas as pd

from ingestion.logging_setup import get_logger
from ingestion.orchestrator import run_ingestion
from features.feature_builder import FeatureBuilder
from model.model_trainer import RiskModelTrainer
from model.portfolio import PortfolioRiskAggregator
from reporting.llm_reporter import LLMReporter
from config import settings

logger = get_logger(__name__)


def main():
    """
    Main orchestration function for the merchant underwriting pipeline.
    
    Runs through all phases:
    1. Ingests data from all sources
    2. Validates and collates data
    3. Engineers features
    4. Trains risk model
    5. Aggregates portfolio-level risk
    6. Generates LLM-powered underwriting report
    """
    logger.info("\n" + "=" * 80)
    logger.info("MERCHANT UNDERWRITING PIPELINE")
    logger.info("=" * 80)
    
    # Phase 1: Data Ingestion
    logger.info("\n[PHASE 1] Ingesting data from all sources...")
    data_dir = Path("data")
    collated_merchants = run_ingestion(data_dir)
    
    if collated_merchants is None:
        logger.error("Ingestion failed; aborting pipeline")
        return
    
    # Phase 2: Feature Engineering
    logger.info("\n[PHASE 2] Engineering features for risk model...")
    collated_df = pd.DataFrame(collated_merchants)
    
    # Define target: high dispute risk if dispute_count >= 3
    # (Using absolute threshold instead of median to avoid data leakage)
    collated_df["high_dispute_risk"] = (collated_df["dispute_count"] >= 3).astype(int)
    
    logger.info(f"  Target distribution: {collated_df['high_dispute_risk'].value_counts().to_dict()}")
    
    # Feature engineering (excludes dispute_count to prevent data leakage)
    feature_builder = FeatureBuilder()
    features = feature_builder.build_features(collated_merchants)
    
    # Keep merchant_id for mapping predictions back
    merchant_ids = collated_df["merchant_id"].values
    
    logger.info(f"✓ Engineered {len(feature_builder.feature_names)} features")
    
    # Phase 3: Model Training
    logger.info("\n[PHASE 3] Training risk classification model...")
    trainer = RiskModelTrainer()
    metrics = trainer.train(features, collated_df["high_dispute_risk"])
    
    logger.info(f"✓ Model trained (AUC: {metrics['auc_score']:.3f})")
    logger.info(f"  Train size: {metrics['train_size']}, Test size: {metrics['test_size']}")
    
    # Phase 4: Generate Predictions
    logger.info("\n[PHASE 4] Generating risk predictions...")
    risk_predictions = trainer.predict(features)
    
    # Create output dataframe with merchant_id and predictions
    collated_df["risk_probability"] = risk_predictions
    
    logger.info(f"✓ Generated predictions for {len(collated_df)} merchants")
    
    # Phase 5: Portfolio Aggregation
    logger.info("\n[PHASE 5] Aggregating portfolio-level risk...")
    portfolio_metrics = PortfolioRiskAggregator.aggregate(collated_df)
    
    logger.info(f"✓ Portfolio summary:")
    logger.info(f"  Total merchants: {portfolio_metrics['total_merchants']}")
    logger.info(f"  High-risk count: {portfolio_metrics['high_risk_count']}")
    logger.info(f"  Expected loss: {portfolio_metrics['expected_loss']:.2f}")
    
    # Phase 6: LLM Report Generation
    logger.info("\n[PHASE 6] Generating LLM-powered underwriting report...")
    reporter = LLMReporter(api_key=settings.openai_api_key)
    
    model_predictions = {"risk_probabilities": risk_predictions.tolist()}
    report = reporter.generate_report(collated_merchants, portfolio_metrics, model_predictions)
    
    if report:
        logger.info("✓ Report generated successfully")
        
        # Save report
        report_path = Path("data/underwriting_report.txt")
        with open(report_path, "w") as f:
            f.write(report)
        logger.info(f"  Saved to {report_path}")
    else:
        logger.warning("⚠ Report generation skipped")
    
    # Save model
    model_path = Path("model/risk_model.pkl")
    model_path.parent.mkdir(exist_ok=True)
    trainer.save_model(str(model_path))
    logger.info(f"✓ Model saved to {model_path}")
    
    # Save collated data with predictions
    collated_df.to_csv("data/collated_merchants_with_predictions.csv", index=False)
    logger.info("✓ Saved collated data with predictions")
    
    logger.info("\n" + "=" * 80)
    logger.info("PIPELINE EXECUTION COMPLETE")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
