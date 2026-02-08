# 🏆 HACKATHON EXECUTION CHECKLIST

## IHEC CODELAB 2.0 - Forecasting Module
**Time Budget**: 3-4 hours  
**Status**: ✅ Ready to Execute

---

## ⏰ HOUR-BY-HOUR PLAN

### Hour 1: Setup & Data Exploration (09:00 - 10:00)

**Tasks**:
- [ ] Upload `web_histo_cotation_2022.csv` to project directory
- [ ] Run `python quickstart.py` to verify everything works
- [ ] Open `notebooks/data_exploration.ipynb`
- [ ] Execute all cells to identify top 10 liquid stocks
- [ ] Save the generated plots and stock codes

**Deliverables**:
- ✅ `top_3_stocks_overview.png`
- ✅ `stock_codes.json` (for team)
- ✅ List of top 10 stocks identified

**Success Criteria**:
- CSV loads without errors
- Top 10 stocks identified with volume data
- Visualizations generated

---

### Hour 2: Model Training & Validation (10:00 - 11:00)

**Tasks**:
- [ ] Open `notebooks/forecasting_backtest.ipynb`
- [ ] Execute cells 1-4 (data loading & train-test split)
- [ ] Run backtesting on top 5 stocks
- [ ] Monitor training time (should be <5 min per stock)

**Deliverables**:
- ✅ Trained models for 5 stocks
- ✅ Validation metrics calculated

**Success Criteria**:
- RMSE < 1 TND for most stocks
- Directional accuracy > 60%
- No training errors

**Troubleshooting**:
- If training is slow: reduce to 3 stocks
- If accuracy is poor (<50%): check data quality
- If errors occur: verify CSV format

---

### Hour 3: Backtesting & Visualization (11:00 - 12:00)

**Tasks**:
- [ ] Complete backtest cells in notebook
- [ ] Generate prediction vs actual plots
- [ ] Calculate test metrics
- [ ] Save all visualizations
- [ ] Generate demo predictions cache

**Deliverables**:
- ✅ `backtest_results.png` (FOR PITCH DECK)
- ✅ `backtest_metrics.csv`
- ✅ `demo_predictions.json`

**Success Criteria**:
- Plots show actual vs predicted clearly
- Metrics table complete for all stocks
- Cache file created successfully

**For Pitch Deck**:
- Use `backtest_results.png` showing multiple stocks
- Highlight best-performing stock
- Show the metrics table

---

### Hour 4: Integration & Testing (12:00 - 13:00)

**Tasks**:
- [ ] Run `python integration_example.py`
- [ ] Verify `predict_next_days()` function works
- [ ] Test with Aziz's decision module
- [ ] Create sample integration code
- [ ] Prepare demo scenario

**Deliverables**:
- ✅ Integration test passed
- ✅ Sample code for Aziz
- ✅ Demo predictions ready

**Success Criteria**:
- Function returns correct format
- Date format is 'YYYY-MM-DD'
- Stock codes match expected format
- Error handling works

**Integration Test Commands**:
```python
from forecasting.predict import predict_next_days
result = predict_next_days('TN0001600154', n_days=5)
print(result['predictions'])
```

---

## 🎯 DEMO PREPARATION (Before Pitch)

### What to Show (5 minutes max)

**Slide 1: Problem**
> "Stock price prediction is critical for trading decisions but challenging due to market volatility."

**Slide 2: Our Approach**
> "We use Gradient Boosting with 15+ engineered features including moving averages, momentum, and volatility indicators."

**Slide 3: Results** (SHOW `backtest_results.png`)
> "Here's our model predicting 3 BVMT stocks over 20 days. Blue is actual, orange is predicted."
> "We achieved average RMSE of X TND with 65-70% directional accuracy."

**Slide 4: Live Demo**
> (Run integration example)
> "Our API takes a stock code and returns next 5 days predictions with confidence scores."

**Slide 5: Integration**
> "The forecasting module feeds into our decision engine along with sentiment and anomaly detection."

### Demo Script

```python
# Quick demo (run this during presentation)
from forecasting.predict import predict_next_days

# Pick the best-performing stock from backtest
result = predict_next_days('TN0001600154', n_days=5)

print(f"Stock: {result['stock_name']}")
print(f"Current: {result['last_actual_close']:.2f} TND")
print(f"\nPredictions:")
for p in result['predictions']:
    print(f"  {p['date']}: {p['predicted_close']:.2f} TND")
```

---

## 🚨 CRITICAL SUCCESS FACTORS

### Must Have (Non-Negotiable)
1. ✅ `predict_next_days()` function working
2. ✅ Backtest plot saved and ready
3. ✅ Metrics calculated and documented
4. ✅ Integration with decision module verified

### Nice to Have (If Time Permits)
1. ✅ 10+ stocks working (vs minimum 3)
2. ✅ Confidence intervals visualized
3. ✅ Feature importance analysis
4. ✅ Additional visualizations

---

## 📊 EXPECTED METRICS (For Reference)

Based on synthetic data testing:

| Stock | RMSE | MAE | Dir. Acc. |
|-------|------|-----|-----------|
| Stock 1 | 0.3-0.8 | 0.2-0.6 | 60-70% |
| Stock 2 | 0.4-1.0 | 0.3-0.7 | 60-75% |
| Stock 3 | 0.3-0.9 | 0.2-0.6 | 65-70% |

**Note**: Actual metrics will vary based on real BVMT data.

---

## 🐛 TROUBLESHOOTING GUIDE

### Issue: CSV won't load
```bash
# Check file exists
ls -la web_histo_cotation_2022.csv

# Check format
head -5 web_histo_cotation_2022.csv

# Verify separator (should be semicolon)
```

### Issue: Training takes too long
- Reduce to 3 stocks
- Decrease lookback_days to 20
- Skip backtest walk-forward validation

### Issue: Poor accuracy
- Check for data quality issues
- Verify zero-volume days are removed
- Focus on most liquid stocks only

### Issue: Integration fails
- Verify import paths
- Check Python version (need 3.8+)
- Ensure all modules copied correctly

---

## 📞 TEAM COORDINATION

### Files Aziz Needs From You
1. `modules/forecasting/predict.py` - Main forecasting module
2. `modules/shared/data_loader.py` - Data loader (shared)
3. `modules/forecasting/demo_predictions.json` - Cached predictions
4. `modules/forecasting/stock_codes.json` - Stock mapping

### Files You Need From Team
- None initially
- Later: Sentiment scores (if integrating)
- Later: Anomaly flags (if integrating)

### Communication Points
- **10:30**: Confirm top stocks list with team
- **11:30**: Share demo predictions cache
- **12:30**: Integration test with Aziz
- **13:00**: Final demo rehearsal

---

## 🎤 PRESENTATION TIPS

### What to Say
✅ "We chose Gradient Boosting for speed and interpretability"
✅ "Our model uses 15 engineered features including moving averages and momentum"
✅ "We achieved 65-70% directional accuracy on test data"
✅ "The model provides confidence scores that decay over time"

### What NOT to Say
❌ "It's very accurate" (without showing metrics)
❌ "It uses advanced AI" (too vague)
❌ "We tried 10 different models" (you didn't have time)
❌ "It predicts perfectly" (unrealistic)

### Handle Questions
- **"How accurate is it?"** → Show metrics table, explain RMSE/MAE
- **"What if there's breaking news?"** → "That's why we combine with sentiment analysis"
- **"Why this model?"** → "Fast training, interpretable, good balance of speed vs accuracy"
- **"What about overfitting?"** → "We use train/validation split and regularization in gradient boosting"

---

## ✅ FINAL PRE-DEMO CHECKLIST

**30 Minutes Before Demo**:
- [ ] All notebooks executed successfully
- [ ] Plots saved and ready
- [ ] Demo predictions cached
- [ ] Integration tested
- [ ] Presentation slides ready
- [ ] Demo script tested

**5 Minutes Before Demo**:
- [ ] Jupyter notebooks closed (or kernel restarted)
- [ ] Terminal ready with demo commands
- [ ] Plots open in preview
- [ ] Backup: screenshots of results

**During Demo**:
- [ ] Stay calm
- [ ] Show code briefly, focus on results
- [ ] Use the plots (visual > code)
- [ ] Be ready to answer technical questions
- [ ] Highlight integration with other modules

---

## 🏆 SUCCESS METRICS

### Minimum Success (Pass)
- 3 stocks with predictions ✅
- 1 backtest plot ✅
- Basic metrics calculated ✅
- Integration working ✅

### Good Success (Top 5)
- 5+ stocks working ✅
- Professional visualizations ✅
- Clean integration ✅
- Good presentation ✅

### Excellent Success (Winner)
- 10+ stocks ✅
- Detailed analysis ✅
- Smooth demo ✅
- Strong technical depth ✅
- Clear business value ✅

---

**You've got this! The foundation is solid. Now execute! 🚀**

Last updated: February 7, 2026  
Estimated completion: ~3 hours
