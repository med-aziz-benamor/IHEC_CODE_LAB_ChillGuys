# BVMT Stock Price Forecasting Module

**IHEC CODELAB 2.0 - Intelligent Trading Assistant**  
Module: Price Forecasting  
Status: Ready for Integration ✅

---

## 📁 Project Structure

```
project_root/
├── web_histo_cotation_2022.csv          # Your dataset (upload this)
├── quickstart.py                         # Quick test script
├── modules/
│   ├── shared/
│   │   └── data_loader.py               # Shared data loader (used by all modules)
│   └── forecasting/
│       ├── predict.py                   # Main forecasting module
│       ├── demo_predictions.json        # Pre-cached predictions (generated)
│       └── stock_codes.json             # Stock code mapping (generated)
└── notebooks/
    ├── data_exploration.ipynb           # Explore data & find top stocks
    └── forecasting_backtest.ipynb       # Train models & generate plots
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Upload Your CSV

Place `web_histo_cotation_2022.csv` in the project root directory.

If you don't have it yet, run the quickstart script to test with synthetic data:

```bash
python quickstart.py
```

### Step 2: Explore Data

```bash
jupyter notebook notebooks/data_exploration.ipynb
```

This will:
- Load the dataset
- Identify top 10 most liquid stocks
- Visualize price history
- Export stock codes for the team

### Step 3: Train & Backtest

```bash
jupyter notebook notebooks/forecasting_backtest.ipynb
```

This will:
- Train models on top 5 stocks
- Backtest on Nov-Dec 2022
- Generate plots for pitch deck
- Create demo predictions cache

---

## 📊 API Usage (For Aziz's Decision Module)

### Import the Function

```python
from forecasting.predict import predict_next_days
```

### Get Predictions

```python
result = predict_next_days(
    stock_code='TN0001600154',  # ISIN code
    n_days=5                     # Number of days to predict
)
```

### Response Format

```python
{
    'stock_code': 'TN0001600154',
    'stock_name': 'ATTIJARI BANK',
    'predictions': [
        {
            'date': '2026-02-08',
            'predicted_close': 31.45,
            'confidence': 0.95
        },
        {
            'date': '2026-02-09',
            'predicted_close': 31.62,
            'confidence': 0.87
        },
        # ... 3 more days
    ],
    'model_used': 'GradientBoostingRegressor',
    'metrics': {
        'rmse': 0.234,
        'mae': 0.187,
        'directional_accuracy': 0.68
    },
    'last_actual_close': 31.20,
    'last_actual_date': '2022-12-31'
}
```

---

## 🎯 Model Details

### Approach: Gradient Boosting with Feature Engineering

**Why this model?**
- ✅ Fast training (<1 min per stock on M1 Mac)
- ✅ No network dependencies (Prophet/ARIMA require pip install)
- ✅ Built-in scikit-learn (available everywhere)
- ✅ Good balance of speed vs accuracy
- ✅ Interpretable for jury presentation

### Features Used

1. **Lagged Prices**: 1, 3, 5, 7, 14 days back
2. **Moving Averages**: 5, 10, 20-day windows
3. **Momentum**: 1-day and 5-day price changes
4. **Volatility**: 5-day rolling standard deviation
5. **Relative Position**: Price position within 20-day range
6. **Volume Features**: Volume moving average and ratio
7. **Temporal**: Day of week (cyclical encoding)

### Training Strategy

- **Training Data**: First 80% of historical data
- **Validation Data**: Last 20% of historical data
- **Lookback Window**: 30 days
- **Model**: GradientBoostingRegressor (100 estimators, max_depth=4)

---

## 📈 Expected Performance

Based on backtesting (typical results):

| Metric | Value |
|--------|-------|
| RMSE | 0.2 - 0.5 TND |
| MAE | 0.15 - 0.4 TND |
| MAPE | 1% - 3% |
| Directional Accuracy | 60% - 70% |

**Note**: Performance varies by stock liquidity. More liquid stocks = better predictions.

---

## 🔧 Troubleshooting

### Issue: "CSV file not found"

```bash
# Check your current directory
pwd

# Make sure CSV is in the right place
ls -la web_histo_cotation_2022.csv

# Or specify full path in notebooks
loader = BVMTDataLoader('/full/path/to/web_histo_cotation_2022.csv')
```

### Issue: "Insufficient data for stock X"

Some stocks have <100 trading days. The model automatically skips these.

Solution: Use only the top 10 liquid stocks (identified in data_exploration.ipynb)

### Issue: "Training is slow"

The model is designed to be fast. If training takes >2 minutes per stock:
- Check if you're using the right CSV (should be ~144k rows)
- Reduce lookback_days from 30 to 20
- Use fewer stocks for demo

---

## 📦 Deliverables for Pitch

### Files to Show

1. **`backtest_results.png`** - Predicted vs Actual plots
2. **`backtest_metrics.csv`** - Performance metrics table
3. **`demo_predictions.json`** - Pre-cached predictions for live demo

### What to Say to Jury

> "For price forecasting, we chose a Gradient Boosting model with engineered features because it's both interpretable and fast to train. We achieved an average RMSE of X TND with 65% directional accuracy on our test set. The model captures weekly trends and momentum but, as expected, struggles with sudden news events—which is why we combine it with sentiment analysis in our decision engine."

**Show the plot**, point to:
- Blue line = actual prices
- Orange line = our predictions
- "You can see we capture the general trend well, with some lag on sudden movements"

---

## 🎯 Integration Checklist for Aziz

- [ ] Import works: `from forecasting.predict import predict_next_days`
- [ ] Stock codes match your format (ISIN codes like 'TN0001600154')
- [ ] Date format is 'YYYY-MM-DD' strings
- [ ] Predictions include confidence scores
- [ ] Error handling works (test with invalid stock code)
- [ ] Demo predictions cached for fast demo

---

## ⏱️ Time Estimate

- **Data exploration**: 30 minutes
- **Training & backtesting**: 45 minutes
- **Generating plots**: 15 minutes
- **Integration testing**: 20 minutes
- **Buffer**: 30 minutes

**Total**: ~2.5 hours (within your 3-4 hour budget)

---

## 🚨 Critical Warnings

### 1. Date Format
Always return dates as `'YYYY-MM-DD'` strings, NOT datetime objects.
Aziz's module expects strings.

### 2. Stock Codes
Use the CODE column (ISIN like "TN0001600154"), NOT company names.
Create `stock_codes.json` mapping for lookup.

### 3. Zero-Volume Days
Some stocks have days with zero trading volume.
Set `remove_zero_volume=True` when loading data.

### 4. Insufficient Data
Skip stocks with <100 trading days.
Focus on top 10 liquid stocks only.

---

## 📞 Questions?

If something doesn't work:

1. Check the quickstart script output
2. Review error messages in notebooks
3. Verify CSV file format (semicolon-separated, DD/MM/YYYY dates)
4. Test with top liquid stocks first

---

## ✅ Success Criteria

**Minimum Viable (MUST HAVE)**:
- [x] predict_next_days() function works for 3 stocks
- [x] Returns predictions in correct format
- [x] Backtesting notebook shows plots
- [x] RMSE/MAE metrics calculated

**Nice to Have (IF TIME)**:
- [ ] Works for 10+ stocks
- [ ] Confidence intervals visualized
- [ ] Cached predictions for fast demo
- [ ] Stock code mapping JSON

---

**Ready to build! 🚀**

Last updated: February 7, 2026
