"""
Isolation Forest model for anomaly detection in BVMT stock data.
Integrated from Module3 for advanced ML-based detection.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pickle
from pathlib import Path
from typing import Optional, Tuple


def get_feature_columns() -> list:
    """
    Get list of feature columns used by the ML model.
    
    Returns:
        List of feature column names
    """
    return [
        'volume',
        'num_transactions',
        'price_change_pct',
        'volume_change_pct',
        'volatility_7d',
        'volume_ratio_7d',
        'volume_ratio_30d',
        'transaction_per_volume',
        'avg_transaction_size',
        'price_volume_corr',
        'high_low_spread_pct',
        'day_of_week'
    ]


class AnomalyDetectionModel:
    """
    Isolation Forest model for detecting trading anomalies.
    Uses unsupervised ML to identify unusual trading patterns.
    """

    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize the anomaly detection model.

        Args:
            contamination: Expected proportion of anomalies (0.01 to 0.5)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.feature_columns = get_feature_columns()
        self.is_trained = False

    def prepare_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepare data for training/prediction.

        Args:
            df: DataFrame with engineered features

        Returns:
            Tuple of (cleaned DataFrame, feature array)
        """
        # Remove rows with missing critical features
        df_clean = df.dropna(subset=self.feature_columns)

        # Filter out zero-volume days (not meaningful for anomaly detection)
        df_clean = df_clean[df_clean['volume'] > 0].copy()

        # Extract features
        X = df_clean[self.feature_columns].values

        # Replace any remaining inf/nan
        X = np.nan_to_num(X, nan=0.0, posinf=1e6, neginf=-1e6)

        return df_clean, X

    def train(self, df: pd.DataFrame, verbose: bool = True) -> dict:
        """
        Train the Isolation Forest model on historical data.

        Args:
            df: DataFrame with stock data (already has engineered features)
            verbose: Print training progress

        Returns:
            Dictionary with training statistics
        """
        if verbose:
            print(f"Training Isolation Forest (contamination={self.contamination})...")

        # Prepare data
        df_clean, X = self.prepare_data(df)

        if verbose:
            print(f"  Training samples: {len(X):,} (from {len(df):,} total rows)")
            print(f"  Features: {len(self.feature_columns)}")

        # Initialize scaler and scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train Isolation Forest
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100,
            max_samples='auto',
            n_jobs=-1,  # Use all CPU cores
            verbose=0
        )

        self.model.fit(X_scaled)
        self.is_trained = True

        # Calculate statistics
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)

        n_anomalies = (predictions == -1).sum()
        anomaly_rate = n_anomalies / len(predictions) * 100

        stats = {
            'total_samples': len(X),
            'n_anomalies': int(n_anomalies),
            'anomaly_rate_pct': float(anomaly_rate),
            'score_mean': float(scores.mean()),
            'score_std': float(scores.std()),
            'score_min': float(scores.min()),
            'score_max': float(scores.max())
        }

        if verbose:
            print(f"  Detected {n_anomalies:,} anomalies ({anomaly_rate:.2f}%)")
            print(f"  Anomaly scores: {stats['score_min']:.3f} to {stats['score_max']:.3f}")

        return stats

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Predict anomalies on new data.

        Args:
            df: DataFrame with stock data (must have engineered features)

        Returns:
            DataFrame with added columns: anomaly_label, anomaly_score
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first.")

        # Prepare data
        df_clean, X = self.prepare_data(df)

        # Scale features
        X_scaled = self.scaler.transform(X)

        # Predict
        predictions = self.model.predict(X_scaled)
        scores = self.model.decision_function(X_scaled)

        # Add to dataframe
        df_clean['anomaly_label'] = predictions  # -1 = anomaly, 1 = normal
        df_clean['anomaly_score'] = scores  # More negative = more anomalous

        return df_clean

    def save(self, filepath: Path):
        """
        Save trained model to disk.

        Args:
            filepath: Path to save the model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns,
            'contamination': self.contamination,
            'random_state': self.random_state
        }

        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"Model saved to {filepath}")

    @classmethod
    def load(cls, filepath: Path) -> 'AnomalyDetectionModel':
        """
        Load trained model from disk.

        Args:
            filepath: Path to the saved model

        Returns:
            Loaded AnomalyDetectionModel instance
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)

        # Create instance
        instance = cls(
            contamination=model_data['contamination'],
            random_state=model_data['random_state']
        )

        # Restore model and scaler
        instance.model = model_data['model']
        instance.scaler = model_data['scaler']
        instance.feature_columns = model_data['feature_columns']
        instance.is_trained = True

        return instance


if __name__ == '__main__':
    # Test loading the model
    MODEL_PATH = Path(__file__).parent.parent.parent / 'models' / 'anomaly_model.pkl'
    
    if MODEL_PATH.exists():
        print("Loading trained model...")
        model = AnomalyDetectionModel.load(MODEL_PATH)
        print(f"✓ Model loaded successfully")
        print(f"  Features: {len(model.feature_columns)}")
        print(f"  Trained: {model.is_trained}")
    else:
        print(f"Model not found at {MODEL_PATH}")
        print("Train the model using Module3 first.")
