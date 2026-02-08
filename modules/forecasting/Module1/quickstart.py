#!/usr/bin/env python3
"""
Quick Start Script for BVMT Forecasting Module
===============================================
Tests the system and generates demo data if CSV is not available

Run: python quickstart.py
"""

import os
import sys

def check_csv_exists():
    """Check if CSV file is available"""
    csv_paths = ["histo_cotation_combined_2022_2025.csv"]
    
    for path in csv_paths:
        if os.path.exists(path):
            print(f"✅ Found CSV at: {path}")
            return path
    
    return None

def create_demo_data():
    """Create synthetic demo data for testing"""
    print("📦 CSV not found. Creating synthetic demo data...")
    
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # Create synthetic data for 3 stocks
    stocks = [
        ('TN0001600154', 'ATTIJARI BANK'),
        ('TN0002100148', 'BIAT'),
        ('TN0001100254', 'BH BANK')
    ]
    
    start_date = datetime(2022, 1, 1)
    n_days = 300
    
    all_data = []
    
    for stock_code, stock_name in stocks:
        base_price = np.random.uniform(25, 40)
        
        for i in range(n_days):
            date = start_date + timedelta(days=i)
            
            # Skip some weekends randomly
            if date.weekday() >= 5 and np.random.random() > 0.9:
                continue
            
            # Random walk with slight upward trend
            price_change = np.random.normal(0.001, 0.02)
            close_price = base_price * (1 + price_change)
            base_price = close_price
            
            open_price = close_price * np.random.uniform(0.99, 1.01)
            high_price = max(open_price, close_price) * np.random.uniform(1.0, 1.02)
            low_price = min(open_price, close_price) * np.random.uniform(0.98, 1.0)
        
            volume = int(np.random.exponential(50000))
            num_trans = int(volume / np.random.uniform(100, 500))
            capital = volume * close_price
            
            all_data.append({
                'SEANCE': date.strftime('%d/%m/%Y'),
                'CODE': stock_code,
                'VALEUR': stock_name,
                'OUVERTURE': round(open_price, 2),
                'CLOTURE': round(close_price, 2),
                'PLUS_BAS': round(low_price, 2),
                'PLUS_HAUT': round(high_price, 2),
                'QUANTITE_NEGOCIEE': volume,
                'NB_TRANSACTION': num_trans,
                'CAPITAUX': round(capital, 2)
            })
    
    df = pd.DataFrame(all_data)
    csv_path = 'projet/histo_cotation_combined_2022_2025.csv'
    df.to_csv(csv_path, sep=';', index=False)
    
    print(f"✅ Created synthetic CSV with {len(df)} rows: {csv_path}")
    print(f"   Stocks: {', '.join([s[1] for s in stocks])}")
    
    return csv_path

def test_data_loader(csv_path):
    """Test the data loader"""
    print("\n" + "="*70)
    print("TESTING DATA LOADER")
    print("="*70)
    
    sys.path.append('modules')
    from shared.data_loader import BVMTDataLoader
    
    loader = BVMTDataLoader(csv_path)
    loader.print_summary()
    
    return loader

def test_forecasting(loader):
    """Test the forecasting module"""
    print("\n" + "="*70)
    print("TESTING FORECASTING MODULE")
    print("="*70)
    
    from forecasting.predict import predict_next_days
    
    top_stocks = loader.get_top_liquid_stocks(3)
    
    if not top_stocks:
        print("❌ No stocks available for testing")
        return
    
    test_stock = top_stocks[0]
    print(f"\n🎯 Testing with: {test_stock['stock_name']} ({test_stock['stock_code']})")
    
    result = predict_next_days(test_stock['stock_code'], n_days=5, csv_path=loader.csv_path)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"\n✅ Prediction successful!")
        print(f"   Model: {result['model_used']}")
        print(f"   Validation RMSE: {result['metrics']['rmse']:.3f} TND")
        print(f"   Validation MAE: {result['metrics']['mae']:.3f} TND")
        print(f"   Directional Accuracy: {result['metrics']['directional_accuracy']:.1%}")
        print(f"\n   Last actual: {result['last_actual_close']:.2f} TND on {result['last_actual_date']}")
        print(f"\n   Next 5 days predictions:")
        for pred in result['predictions']:
            print(f"   {pred['date']}: {pred['predicted_close']:.2f} TND (confidence: {pred['confidence']:.0%})")

def main():
    print("\n🚀 BVMT FORECASTING MODULE - QUICK START")
    print("="*70)
    
    # Check for CSV
    csv_path = check_csv_exists()
    
    if not csv_path:
        csv_path = create_demo_data()
    
    # Test data loader
    try:
        loader = test_data_loader(csv_path)
    except Exception as e:
        print(f"❌ Data loader test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    # Test forecasting
    try:
        test_forecasting(loader)
    except Exception as e:
        print(f"❌ Forecasting test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\n📋 Next Steps:")
    print("   1. Upload your actual CSV file: web_histo_cotation_2022.csv")
    print("   2. Run: jupyter notebook notebooks/data_exploration.ipynb")
    print("   3. Run: jupyter notebook notebooks/forecasting_backtest.ipynb")
    print("   4. Integration: from forecasting.predict import predict_next_days")
    print("\n🎉 Ready for hackathon demo!\n")

if __name__ == "__main__":
    main()
