# modules/forecasting/generate_demo_cache.py
"""Pre-generate predictions for demo day safety."""

from modules.forecasting.predict import batch_predict
from modules.shared.data_loader import get_most_liquid_stocks

def main():
    print("Generating demo predictions cache...")

    liquid = get_most_liquid_stocks(15)
    codes = liquid["code"].tolist()

    print("Selected stocks:")
    print(liquid[["name", "code", "trading_days", "total_volume"]].head(15).to_string(index=False))

    results = batch_predict(
        stock_codes=codes,
        n_days=5,
        cache_path="modules/forecasting/demo_predictions.json"
    )

    ok = [c for c, r in results.items() if isinstance(r, dict) and "error" not in r]
    print(f"\nSuccess: {len(ok)}/{len(codes)}")
    print("Cache saved to: modules/forecasting/demo_predictions.json")

if __name__ == "__main__":
    main()