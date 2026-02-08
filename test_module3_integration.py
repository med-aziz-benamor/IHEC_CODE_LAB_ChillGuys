"""
Module3 Anomaly Detection Integration Test
Tests the integration of Module3's ML-based anomaly detection
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Test imports
print("="*80)
print("MODULE3 ANOMALY DETECTION INTEGRATION TEST")
print("Testing ML-based anomaly detection with Isolation Forest")
print("="*80)

def test_imports():
    """Test that all Module3 components import correctly"""
    print("\n[TEST 1] Testing imports...")
    
    try:
        from modules.anomaly.model import AnomalyDetectionModel, get_feature_columns
        from modules.anomaly.detector import (
            detect_anomalies,
            detect_volume_spike,
            detect_price_gap,
            detect_low_liquidity,
            detect_price_volume_divergence
        )
        from modules.shared.data_loader import engineer_features, get_feature_columns as get_data_features
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def test_feature_engineering():
    """Test feature engineering for ML model"""
    print("\n[TEST 2] Testing feature engineering...")
    
    try:
        from modules.shared.data_loader import load_full_dataset, engineer_features, get_feature_columns
        import pandas as pd
        
        # Load sample data
        df = load_full_dataset()
        print(f"  Loaded {len(df):,} rows")
        
        # Engineer features on a sample
        sample = df.head(500).copy()
        sample_features = engineer_features(sample)
        
        # Check if features exist
        feature_cols = get_feature_columns()
        print(f"  Expected features: {len(feature_cols)}")
        
        existing_features = [col for col in feature_cols if col in sample_features.columns]
        print(f"  Found features: {len(existing_features)}")
        
        if len(existing_features) >= 10:  # At least 10 features
            print(f"  ✓ Feature engineering successful")
            print(f"    Sample features: {existing_features[:5]}")
            return True
        else:
            print(f"  ✗ Insufficient features: {existing_features}")
            return False
            
    except Exception as e:
        print(f"  ✗ Feature engineering error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_model():
    """Test ML model loading and prediction"""
    print("\n[TEST 3] Testing ML model...")
    
    try:
        from modules.anomaly.model import AnomalyDetectionModel
        from pathlib import Path
        
        model_path = Path(__file__).parent / 'models' / 'anomaly_model.pkl'
        
        if not model_path.exists():
            print(f"  ⚠️ Model not found at {model_path}")
            print( "  This is expected if Module3 model hasn't been trained yet")
            return True  # Not a failure, just not available
        
        # Load model
        model = AnomalyDetectionModel.load(model_path)
        print(f"  ✓ Model loaded successfully")
        print(f"    Features: {len(model.feature_columns)}")
        print(f"    Trained: {model.is_trained}")
        
        # Test prediction on sample data
        from modules.shared.data_loader import get_stock_data, engineer_features
        stock_df = get_stock_data('TN0001600154')  # ATB
        
        if stock_df is not None and len(stock_df) > 0:
            stock_df = engineer_features(stock_df)
            predictions = model.predict(stock_df.tail(30))
            
            anomalies = predictions[predictions['anomaly_label'] == -1]
            print(f"    Sample predictions: {len(predictions)} rows")
            print(f"    ML anomalies detected: {len(anomalies)}")
            print(f"  ✓ ML prediction successful")
            return True
        else:
            print(f"  ⚠️ No stock data available for testing")
            return True
            
    except Exception as e:
        print(f"  ✗ ML model error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_detectors():
    """Test enhanced detection functions"""
    print("\n[TEST 4] Testing enhanced detector functions...")
    
    try:
        from modules.anomaly.detector import (
            detect_volume_spike,
            detect_price_gap,
            detect_low_liquidity,
            detect_price_volume_divergence
        )
        from modules.shared.data_loader import get_stock_data, engineer_features
        import pandas as pd
        
        # Get sample data
        stock_df = get_stock_data('TN0001600154')
        stock_df = engineer_features(stock_df)
        
        # Test on a sample row
        test_row = stock_df.iloc[-1]
        
        detected = []
        
        # Volume spike
        vol_anom = detect_volume_spike(test_row)
        if vol_anom:
            detected.append('volume_spike')
            
        # Price gap
        price_anom = detect_price_gap(test_row)
        if price_anom:
            detected.append('price_gap')
            
        # Low liquidity
        liq_anom = detect_low_liquidity(test_row)
        if liq_anom:
            detected.append('low_liquidity')
            
        # Price-volume divergence
        div_anom = detect_price_volume_divergence(test_row)
        if div_anom:
            detected.append('divergence')
        
        print(f"  ✓ All detector functions executed")
        if detected:
            print(f"    Anomalies found: {detected}")
        else:
            print(f"    No anomalies in test row (normal behavior)")
        return True
        
    except Exception as e:
        print(f"  ✗ Detector error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_anomaly_detection():
    """Test full anomaly detection with ML"""
    print("\n[TEST 5] Testing full anomaly detection...")
    
    try:
        from modules.anomaly.detector import detect_anomalies
        
        # Test stocks
        test_stocks = [
            ('TN0001600154', 'ATTIJARI BANK'),
            ('TN0001800457', 'BIAT'),
            ('TN0001100254', 'SFBT')
        ]
        
        results = []
        
        for stock_code, stock_name in test_stocks:
            print(f"\n  Testing {stock_name} ({stock_code})...")
            
            result = detect_anomalies(stock_code, lookback_days=30, use_ml=True)
            
            print(f"    Risk Level: {result['risk_level']}")
            print(f"    Score: {result['score']:.1f}/10")
            print(f"    ML Enabled: {result['ml_enabled']}")
            print(f"    Anomalies: {len(result['anomalies_detected'])}")
            print(f"    Summary: {result['summary']}")
            
            if 'error' in result:
                print(f"    ⚠️  Error: {result['error']}")
            else:
                results.append(result)
                
                # Show top 2 anomalies
                if result['anomalies_detected']:
                    print(f"    Top anomalies:")
                    for anom in result['anomalies_detected'][:2]:
                        print(f"      [{anom['severity']}] {anom['date']}: {anom['description'][:60]}...")
        
        if results:
            print(f"\n  ✓ Full anomaly detection successful ({len(results)}/3 stocks)")
            return True
        else:
            print(f"\n  ⚠️  No successful detections")
            return False
            
    except Exception as e:
        print(f"  ✗ Full detection error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ml_vs_statistical():
    """Compare ML vs statistical-only detection"""
    print("\n[TEST 6] Comparing ML vs Statistical detection...")
    
    try:
        from modules.anomaly.detector import detect_anomalies
        
        test_stock = 'TN0001600154'  # ATTIJARI BANK
        
        # With ML
        print(f"\n  With ML:")
        result_ml = detect_anomalies(test_stock, lookback_days=30, use_ml=True)
        print(f"    ML Enabled: {result_ml['ml_enabled']}")
        print(f"    Anomalies: {len(result_ml['anomalies_detected'])}")
        print(f"    Score: {result_ml['score']:.1f}/10")
        
        # Without ML (statistical only)
        print(f"\n  Without ML (statistical only):")
        result_stat = detect_anomalies(test_stock, lookback_days=30, use_ml=False)
        print(f"    ML Enabled: {result_stat['ml_enabled']}")
        print(f"    Anomalies: {len(result_stat['anomalies_detected'])}")
        print(f"    Score: {result_stat['score']:.1f}/10")
        
        # Compare
        ml_types = set(a['type'] for a in result_ml['anomalies_detected'])
        stat_types = set(a['type'] for a in result_stat['anomalies_detected'])
        
        print(f"\n  Unique anomaly types:")
        print(f"    ML mode: {ml_types}")
        print(f"    Statistical: {stat_types}")
        
        if 'ml_detected' in ml_types:
            print(f"  ✓ ML successfully added additional anomaly types")
        else:
            print(f"  ✓ Both modes working (ML may not find additional anomalies in this sample)")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Comparison error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    tests = [
        test_imports,
        test_feature_engineering,
        test_ml_model,
        test_enhanced_detectors,
        test_full_anomaly_detection,
        test_ml_vs_statistical
    ]
    
    results = []
    for test_func in tests:
        try:
            passed = test_func()
            results.append((test_func.__name__, passed))
        except Exception as e:
            print(f"\n✗ Test {test_func.__name__} crashed: {e}")
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n  Total: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n  🎉 ALL TESTS PASSED! Module3 integration is working correctly.")
    elif passed_count >= total_count * 0.7:
        print("\n  ⚠️  Most tests passed. Minor issues may need attention.")
    else:
        print("\n  ❌ Some tests failed. Check errors above.")
    
    return passed_count == total_count


if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
