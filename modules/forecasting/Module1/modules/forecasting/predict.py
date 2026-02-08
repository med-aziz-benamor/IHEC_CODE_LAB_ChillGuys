"""
BVMT Forecasting - multi-model with rolling training window
Train on last N days (default 50) and forecast next 1-5 trading days.

Models:
- arima (always available)
- prophet (optional)
- rf (optional, scikit-learn)
- xgb (optional, xgboost)
- lstm (optional, tensorflow)

Run:
  cd C:\\Users\\rania\\Downloads\\ihec\\projet
  python -m modules.forecasting.predict
"""

from __future__ import annotations

import warnings
warnings.filterwarnings("ignore")

import time
import os
import json
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import numpy as np
import pandas as pd

from statsmodels.tsa.arima.model import ARIMA

from modules.shared.data_loader import (
    get_stock_data,
    get_stock_name,
    get_most_liquid_stocks,
)

# Optional deps
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except Exception:
    PROPHET_AVAILABLE = False

SKLEARN_AVAILABLE = False
XGB_AVAILABLE = False
TF_AVAILABLE = False


# ---------------------------
# Utilities
# ---------------------------

def next_trading_days(last_date: pd.Timestamp, n_days: int) -> List[pd.Timestamp]:
    """Next n trading days (Mon-Fri)."""
    dates: List[pd.Timestamp] = []
    cur = pd.Timestamp(last_date)
    while len(dates) < n_days:
        cur += timedelta(days=1)
        if cur.weekday() < 5:
            dates.append(cur)
    return dates


def calculate_metrics(actual: pd.Series, predicted: pd.Series) -> Dict[str, float]:
    actual = pd.Series(actual).astype(float).reset_index(drop=True)
    predicted = pd.Series(predicted).astype(float).reset_index(drop=True)

    n = min(len(actual), len(predicted))
    actual = actual.iloc[-n:].values
    predicted = predicted.iloc[-n:].values

    rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
    mae = float(np.mean(np.abs(actual - predicted)))
    mape = float(np.mean(np.abs((actual - predicted) / np.maximum(np.abs(actual), 1e-6))) * 100.0)

    if len(actual) >= 2:
        actual_dir = np.diff(actual) > 0
        pred_dir = np.diff(predicted) > 0
        directional_accuracy = float(np.mean(actual_dir == pred_dir) * 100.0)
    else:
        directional_accuracy = float("nan")

    return {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "mape": round(mape, 2),
        "directional_accuracy": round(directional_accuracy, 2),
    }


def make_lag_features(close: pd.Series, n_lags: int = 10) -> pd.DataFrame:
    """Time series -> supervised features."""
    s = pd.Series(close).astype(float).reset_index(drop=True)
    df = pd.DataFrame({"y": s})

    for i in range(1, n_lags + 1):
        df[f"lag_{i}"] = df["y"].shift(i)

    df["ret_1"] = df["y"].pct_change()
    df["ma_5"] = df["y"].rolling(5).mean()
    df["ma_10"] = df["y"].rolling(10).mean()
    df["std_5"] = df["y"].rolling(5).std()
    df["std_10"] = df["y"].rolling(10).std()
    return df


def build_supervised(close: pd.Series, n_lags: int = 10):
    feat = make_lag_features(close, n_lags=n_lags).dropna().reset_index(drop=True)
    X = feat.drop(columns=["y"])
    y = feat["y"]
    return X, y


def approx_confidence(yhat: float, lo: float, hi: float, avg_price: float) -> float:
    """Heuristic confidence based on interval width."""
    if avg_price <= 0:
        return 0.6
    width = float(hi - lo)
    conf = 1.0 - width / (2.0 * avg_price)
    return float(np.clip(conf, 0.5, 0.95))


# ---------------------------
# Model wrapper
# ---------------------------

@dataclass
class FitResult:
    model_used: str
    training_time_sec: float


class ForecastingModel:
    """
    model_type:
      - "arima"
      - "prophet" (optional)
      - "rf"      (optional)
      - "xgb"     (optional)
      - "lstm"    (optional)
      - "auto"    => choose best among available (quick validation)
    """

    def __init__(self, model_type: str = "auto", max_train_time: int = 15, n_lags: int = 10):
        self.model_type = model_type
        self.max_train_time = max_train_time
        self.n_lags = n_lags

        self.model: Any = None
        self.used_model: Optional[str] = None
        self.training_time_sec: float = 0.0

        self.last_df: Optional[pd.DataFrame] = None
        self.resid_std: Optional[float] = None  # for ML interval

        # LSTM
        self.lstm_scaler: Optional[Any] = None
        self.lstm_steps: int = 20

    # ---- train ----

    def _train_arima(self, df: pd.DataFrame):
        start = time.time()
        fitted = ARIMA(df["close"].astype(float), order=(5, 1, 0)).fit()
        self.training_time_sec = time.time() - start
        self.resid_std = None
        return fitted

    def _train_prophet(self, df: pd.DataFrame):
        if not PROPHET_AVAILABLE:
            raise ImportError("Prophet not installed")
        p_df = df[["date", "close"]].rename(columns={"date": "ds", "close": "y"})
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
            interval_width=0.95,
            changepoint_prior_scale=0.05,
        )
        model.add_seasonality(name="monthly", period=30.5, fourier_order=5)

        start = time.time()
        model.fit(p_df)
        self.training_time_sec = time.time() - start
        self.resid_std = None
        return model

    def _train_rf(self, df: pd.DataFrame):
        try:
            from sklearn.ensemble import RandomForestRegressor
        except Exception as e:
            raise ImportError("scikit-learn not installed") from e
        X, y = build_supervised(df["close"], n_lags=self.n_lags)
        model = RandomForestRegressor(n_estimators=400, random_state=42, n_jobs=-1)
        start = time.time()
        model.fit(X, y)
        self.training_time_sec = time.time() - start
        resid = y.values - model.predict(X)
        self.resid_std = float(np.nanstd(resid))
        return model

    def _train_xgb(self, df: pd.DataFrame):
        try:
            from xgboost import XGBRegressor
        except Exception as e:
            raise ImportError("xgboost not installed") from e
        X, y = build_supervised(df["close"], n_lags=self.n_lags)
        model = XGBRegressor(
            n_estimators=600,
            learning_rate=0.03,
            max_depth=4,
            subsample=0.9,
            colsample_bytree=0.9,
            reg_lambda=1.0,
            random_state=42,
        )
        start = time.time()
        model.fit(X, y)
        self.training_time_sec = time.time() - start
        resid = y.values - model.predict(X)
        self.resid_std = float(np.nanstd(resid))
        return model

    def _train_lstm(self, df: pd.DataFrame):
        try:
            from sklearn.preprocessing import MinMaxScaler
            from tensorflow.keras import Sequential
            from tensorflow.keras.layers import LSTM, Dense
        except Exception as e:
            raise ImportError("tensorflow not installed") from e
        close = df["close"].astype(float).values.reshape(-1, 1)
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(close)

        steps = self.lstm_steps
        X, y = [], []
        for i in range(steps, len(scaled)):
            X.append(scaled[i - steps:i, 0])
            y.append(scaled[i, 0])
        X = np.array(X).reshape(-1, steps, 1)
        y = np.array(y)

        model = Sequential([LSTM(32, input_shape=(steps, 1)), Dense(1)])
        model.compile(optimizer="adam", loss="mse")

        start = time.time()
        model.fit(X, y, epochs=15, batch_size=32, verbose=0)
        self.training_time_sec = time.time() - start
        self.lstm_scaler = scaler
        self.resid_std = None
        return model

    # ---- predict ----

    def _predict_arima(self, n_days: int) -> pd.DataFrame:
        assert self.last_df is not None
        fc = self.model.get_forecast(steps=n_days)
        mean = fc.predicted_mean
        conf = fc.conf_int()
        dates = next_trading_days(self.last_df["date"].iloc[-1], n_days)
        return pd.DataFrame({
            "date": dates,
            "predicted_close": mean.values,
            "lower_bound": conf.iloc[:, 0].values,
            "upper_bound": conf.iloc[:, 1].values,
        })

    def _predict_prophet(self, n_days: int) -> pd.DataFrame:
        model = self.model
        future = model.make_future_dataframe(periods=n_days)
        fc = model.predict(future).tail(n_days)
        out = fc.rename(columns={
            "ds": "date",
            "yhat": "predicted_close",
            "yhat_lower": "lower_bound",
            "yhat_upper": "upper_bound",
        })[["date", "predicted_close", "lower_bound", "upper_bound"]]
        return out

    def _predict_ml_recursive(self, n_days: int) -> pd.DataFrame:
        assert self.last_df is not None
        history = list(self.last_df["close"].astype(float).values)
        dates = next_trading_days(self.last_df["date"].iloc[-1], n_days)

        preds, lows, highs = [], [], []
        avg_price = float(np.nanmean(history))

        for _ in range(n_days):
            X, _ = build_supervised(pd.Series(history), n_lags=self.n_lags)
            x_last = X.iloc[[-1]]
            yhat = float(self.model.predict(x_last)[0])
            preds.append(yhat)
            history.append(yhat)

            if self.resid_std is None or np.isnan(self.resid_std):
                lo, hi = yhat * 0.97, yhat * 1.03
            else:
                lo, hi = yhat - 1.96 * self.resid_std, yhat + 1.96 * self.resid_std

            lows.append(lo)
            highs.append(hi)

        return pd.DataFrame({
            "date": dates,
            "predicted_close": preds,
            "lower_bound": lows,
            "upper_bound": highs,
        })

    def _predict_lstm_recursive(self, n_days: int) -> pd.DataFrame:
        assert self.last_df is not None
        assert self.lstm_scaler is not None

        close = self.last_df["close"].astype(float).values.reshape(-1, 1)
        scaled = self.lstm_scaler.transform(close).flatten().tolist()

        steps = self.lstm_steps
        seq = scaled[-steps:]

        preds_scaled = []
        for _ in range(n_days):
            x = np.array(seq[-steps:]).reshape(1, steps, 1)
            yhat_s = float(self.model.predict(x, verbose=0)[0, 0])
            preds_scaled.append(yhat_s)
            seq.append(yhat_s)

        preds = self.lstm_scaler.inverse_transform(np.array(preds_scaled).reshape(-1, 1)).flatten()
        dates = next_trading_days(self.last_df["date"].iloc[-1], n_days)

        return pd.DataFrame({
            "date": dates,
            "predicted_close": preds,
            "lower_bound": preds * 0.97,
            "upper_bound": preds * 1.03,
        })

    # ---- fit routing + optional auto selection ----

    def fit(self, df: pd.DataFrame) -> FitResult:
        self.last_df = df.copy()
        self.model = None
        self.used_model = None
        self.resid_std = None

        if self.model_type != "auto":
            self._fit_one(df, self.model_type)
            return FitResult(self.used_model, self.training_time_sec)

        # AUTO: quick choose best model on small validation slice
        # Use last 10 points of df as quick validation (within the 50-day window).
        quick_val = min(10, max(5, len(df) // 5))
        train_part = df.iloc[:-quick_val].copy()
        val_part = df.iloc[-quick_val:].copy()

        # candidate list depending on availability
        if os.getenv("BVMT_FORECAST_ENABLE_HEAVY") == "1":
            global SKLEARN_AVAILABLE, XGB_AVAILABLE, TF_AVAILABLE
            if not SKLEARN_AVAILABLE:
                try:
                    import sklearn  # noqa: F401
                    SKLEARN_AVAILABLE = True
                except Exception:
                    SKLEARN_AVAILABLE = False
            if not XGB_AVAILABLE:
                try:
                    import xgboost  # noqa: F401
                    XGB_AVAILABLE = True
                except Exception:
                    XGB_AVAILABLE = False
            if not TF_AVAILABLE:
                try:
                    import tensorflow  # noqa: F401
                    TF_AVAILABLE = True
                except Exception:
                    TF_AVAILABLE = False
        candidates = ["arima"]
        if SKLEARN_AVAILABLE:
            candidates.append("rf")
        if XGB_AVAILABLE:
            candidates.append("xgb")
        if PROPHET_AVAILABLE:
            candidates.append("prophet")
        if TF_AVAILABLE:
            candidates.append("lstm")

        best = None
        best_rmse = float("inf")
        best_time = None

        for mt in candidates:
            try:
                tmp = ForecastingModel(model_type=mt, max_train_time=self.max_train_time, n_lags=self.n_lags)
                tmp._fit_one(train_part, mt)
                pred = tmp.predict(len(val_part))
                rmse = calculate_metrics(val_part["close"], pred["predicted_close"])["rmse"]
                if rmse < best_rmse:
                    best_rmse = rmse
                    best = mt
                    best_time = tmp.training_time_sec
            except Exception:
                continue

        if best is None:
            best = "arima"

        self._fit_one(df, best)
        return FitResult(self.used_model, self.training_time_sec)

    def _fit_one(self, df: pd.DataFrame, mt: str):
        if mt == "arima":
            self.model = self._train_arima(df)
            self.used_model = "arima"
            return
        if mt == "prophet":
            m = self._train_prophet(df)
            if self.training_time_sec > self.max_train_time:
                raise TimeoutError(f"Prophet too slow ({self.training_time_sec:.1f}s)")
            self.model = m
            self.used_model = "prophet"
            return
        if mt == "rf":
            self.model = self._train_rf(df)
            self.used_model = "rf"
            return
        if mt == "xgb":
            self.model = self._train_xgb(df)
            self.used_model = "xgb"
            return
        if mt == "lstm":
            self.model = self._train_lstm(df)
            self.used_model = "lstm"
            return
        raise ValueError(f"Unknown model_type: {mt}")

    def predict(self, n_days: int = 5) -> pd.DataFrame:
        if self.used_model == "arima":
            return self._predict_arima(n_days)
        if self.used_model == "prophet":
            return self._predict_prophet(n_days)
        if self.used_model in ("rf", "xgb"):
            return self._predict_ml_recursive(n_days)
        if self.used_model == "lstm":
            return self._predict_lstm_recursive(n_days)
        raise RuntimeError("Model not fitted.")


# ---------------------------
# Main API
# ---------------------------

def predict_next_days(
    stock_code: str,
    n_days: int = 5,
    model_type: str = "auto",
    train_start: Optional[str] = None,
    train_end: Optional[str] = None,
    min_volume: int = 1,
    train_window_days: int = 900,   # <-- IMPORTANT: rolling window
    val_horizon_days: int = 10     # rolling validation horizon
) -> Dict:
    # Load ALL history (cleaned) then take last N days for training
    df_all = get_stock_data(stock_code, start_date=train_start, end_date=train_end, min_volume=min_volume)

    if len(df_all) < train_window_days:
        raise ValueError(f"Insufficient data: {len(df_all)} rows < train_window_days={train_window_days}")

    df_train = df_all.tail(train_window_days).copy()

    fm = ForecastingModel(model_type=model_type)
    fit_res = fm.fit(df_train)

    pred_df = fm.predict(n_days).copy()

    avg_price = float(df_train["close"].mean())
    pred_df["confidence"] = [
        approx_confidence(float(y), float(lo), float(hi), avg_price)
        for y, lo, hi in zip(pred_df["predicted_close"], pred_df["lower_bound"], pred_df["upper_bound"])
    ]

    predictions = []
    for _, r in pred_df.iterrows():
        d = r["date"]
        d_str = pd.Timestamp(d).strftime("%Y-%m-%d") if isinstance(d, (pd.Timestamp, datetime)) else str(d)[:10]
        predictions.append({
            "date": d_str,
            "predicted_close": round(float(r["predicted_close"]), 3),
            "confidence": round(float(r["confidence"]), 3),
            "lower_bound": round(float(r["lower_bound"]), 3),
            "upper_bound": round(float(r["upper_bound"]), 3),
        })

    # Rolling validation (coherent with rolling training):
    # predict the last k days using the k days just before them (window=N)
    metrics: Dict[str, float]
    k = int(val_horizon_days)

    if len(df_all) >= train_window_days + k:
        val_df = df_all.tail(k).copy()
        train_for_val = df_all.iloc[-(train_window_days + k):-k].copy()

        fm_val = ForecastingModel(model_type=fm.used_model or model_type)
        fm_val.fit(train_for_val)
        val_pred = fm_val.predict(len(val_df))

        metrics = calculate_metrics(val_df["close"], val_pred["predicted_close"])
    else:
        # fallback: small split within df_train
        val_size = max(min(10, len(df_train)//5), 5)
        train_part = df_train.iloc[:-val_size].copy()
        val_df = df_train.iloc[-val_size:].copy()

        fm_val = ForecastingModel(model_type=fm.used_model or model_type)
        fm_val.fit(train_part)
        val_pred = fm_val.predict(len(val_df))
        metrics = calculate_metrics(val_df["close"], val_pred["predicted_close"])

    metrics["training_time_sec"] = round(float(fit_res.training_time_sec), 3)
    metrics["data_points_used"] = int(len(df_train))
    metrics["train_window_days"] = int(train_window_days)
    metrics["val_horizon_days"] = int(k)

    last_actual = float(df_train["close"].iloc[-1])
    last_pred = float(predictions[-1]["predicted_close"])
    trend = "upward" if last_pred > last_actual * 1.01 else "downward" if last_pred < last_actual * 0.99 else "sideways"

    return {
        "stock_code": stock_code,
        "stock_name": get_stock_name(stock_code),
        "predictions": predictions,
        "model_used": fit_res.model_used,
        "metrics": metrics,
        "last_actual_close": round(last_actual, 3),
        "trend": trend,
        "prediction_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def benchmark_models(
    stock_code: str,
    model_types: Optional[List[str]] = None,
    min_volume: int = 1,
    train_window_days: int = 900,
    val_horizon_days: int = 10,
) -> pd.DataFrame:
    """Compare models on same rolling split: train on N days, test on next k days (historically)."""
    if model_types is None:
        model_types = ["arima", "rf", "xgb", "prophet", "lstm"]

    df_all = get_stock_data(stock_code, min_volume=min_volume)
    if len(df_all) < train_window_days + val_horizon_days:
        raise ValueError("Not enough data for rolling benchmark")

    train_df = df_all.iloc[-(train_window_days + val_horizon_days):-val_horizon_days].copy()
    test_df = df_all.tail(val_horizon_days).copy()

    rows = []
    for mt in model_types:
        try:
            fm = ForecastingModel(model_type=mt)
            fit_res = fm.fit(train_df)
            pred = fm.predict(len(test_df))
            met = calculate_metrics(test_df["close"], pred["predicted_close"])
            met["model"] = fit_res.model_used
            met["train_time_sec"] = round(float(fit_res.training_time_sec), 3)
            rows.append(met)
        except Exception as e:
            rows.append({"model": mt, "error": str(e)})

    return pd.DataFrame(rows)


def batch_predict(
    stock_codes: List[str],
    n_days: int = 5,
    cache_path: str = "modules/forecasting/demo_predictions.json",
    model_type: str = "auto",
    train_window_days: int = 900
) -> Dict[str, Dict]:
    results: Dict[str, Dict] = {}

    for code in stock_codes:
        try:
            print(f"Predicting {code} ...")
            r = predict_next_days(code, n_days=n_days, model_type=model_type, train_window_days=train_window_days)
            results[code] = r
            print(f"  ✓ {r['stock_name']} | model={r['model_used']} | RMSE={r['metrics']['rmse']} | trend={r['trend']}")
        except Exception as e:
            print(f"  ✗ Failed for {code}: {e}")
            results[code] = {"error": str(e)}

    Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return results


def load_cached_predictions(cache_path: str = "modules/forecasting/demo_predictions.json") -> Dict:
    with open(cache_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_forecast(stock_code: str, n_days: int = 5) -> Dict:
    """Decision engine wrapper: live then cache."""
    try:
        return predict_next_days(stock_code, n_days=n_days)
    except Exception as e:
        print(f"Live prediction failed: {e}. Using cache...")
        cache = load_cached_predictions()
        if stock_code in cache and "error" not in cache[stock_code]:
            return cache[stock_code]
        raise


# ---------------------------
# CLI test
# ---------------------------

if __name__ == "__main__":
    print("Testing forecasting module (rolling window = 50 days)...")

    # pick a liquid stock automatically
    liq = get_most_liquid_stocks(5)
    test_code = liq.iloc[1]["code"]
    print(f"Test stock: {liq.iloc[1]['name']} ({test_code})")

    print("\nBenchmark (rolling):")
    bm = benchmark_models(test_code, model_types=["arima", "rf", "xgb", "prophet", "lstm"], train_window_days=900, val_horizon_days=10)
    print(bm.to_string(index=False))

    print("\nLive prediction (next 5 days):")
    res = predict_next_days(test_code, n_days=5, model_type="auto", train_window_days=900)
    print(f"Stock: {res['stock_name']} ({res['stock_code']}) | model_used={res['model_used']}")
    for p in res["predictions"]:
        print(f"  {p['date']}: {p['predicted_close']} (conf {p['confidence']})")
    print("Metrics:", res["metrics"])
