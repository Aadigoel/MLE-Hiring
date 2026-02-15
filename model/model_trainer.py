"""Model training and risk prediction."""

import logging
import pandas as pd
import numpy as np
from typing import Tuple, Dict
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import pickle

from config import settings

logger = logging.getLogger(__name__)


class RiskModelTrainer:
    """Train and evaluate risk classification model."""

    def __init__(self, random_seed: int = settings.random_seed):
        """
        Initialize model trainer.
        
        Args:
            random_seed: Random seed for reproducibility
        """
        self.random_seed = random_seed
        self.model = None
        self.scaler = None
        self.feature_names = []
        np.random.seed(random_seed)

    def train(
        self,
        features_df: pd.DataFrame,
        target_series: pd.Series,
        test_size: float = settings.test_size,
    ) -> Dict:
        """
        Train logistic regression model for risk classification.
        
        Args:
            features_df: Feature dataframe
            target_series: Target variable (high_dispute_risk)
            test_size: Proportion of data for testing
            
        Returns:
            Dict with training metrics
        """
        logger.info("Training risk classification model")
        
        self.feature_names = features_df.columns.tolist()
        
        # Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            features_df,
            target_series,
            test_size=test_size,
            random_state=self.random_seed,
            stratify=target_series,
        )
        
        logger.info(f"Train set: {len(X_train)}, Test set: {len(X_test)}")
        logger.info(f"Target distribution - Train: {y_train.value_counts().to_dict()}")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model with balanced class weights to handle imbalance
        self.model = LogisticRegression(
            random_state=self.random_seed,
            max_iter=1000,
            class_weight='balanced',  # Automatically weight inversely to class frequency
        )
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        metrics = {
            "train_size": len(X_train),
            "test_size": len(X_test),
            "auc_score": roc_auc_score(y_test, y_pred_proba),
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }
        
        logger.info(f"Model AUC: {metrics['auc_score']:.3f}")
        logger.info(f"Classification Report:\n{classification_report(y_test, y_pred)}")
        
        return metrics

    def predict(self, features_df: pd.DataFrame) -> np.ndarray:
        """
        Predict risk for new data.
        
        Args:
            features_df: Feature dataframe
            
        Returns:
            Array of risk probabilities
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(features_df)
        return self.model.predict_proba(X_scaled)[:, 1]

    def save_model(self, path: str):
        """Save model and scaler to disk."""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        logger.info(f"Saving model to {path}")
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler}, f)

    def load_model(self, path: str):
        """Load model and scaler from disk."""
        logger.info(f"Loading model from {path}")
        with open(path, "rb") as f:
            data = pickle.load(f)
            self.model = data["model"]
            self.scaler = data["scaler"]
