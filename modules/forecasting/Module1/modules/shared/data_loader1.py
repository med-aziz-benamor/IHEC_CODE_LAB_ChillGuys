"""
Shared Data Loader for BVMT Stock Data
=======================================
Used by all modules: forecasting, sentiment, anomaly detection, decision engine

Author: Forecasting Team
Hackathon: IHEC CODELAB 2.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
import os


class BVMTDataLoader:
    """
    Loads and processes BVMT historical stock data from CSV.
    
    Handles:
    - Date parsing (DD/MM/YYYY format)
    - Semicolon-separated values
    - Zero-volume days filtering
    - Missing data handling
    """
    
    def __init__(self, csv_path: str = 'web_histo_cotation_2022.csv'):
        """
        Initialize the data loader.
        
        Args:
            csv_path: Path to the CSV file
        """
        self.csv_path = csv_path
        self.df = None
        self.stock_metadata = {}
        self._load_data()
        
    def _load_data(self):
        """Load and preprocess the CSV data."""
        try:
            # Load CSV - try different separators
            try:
                self.df = pd.read_csv(self.csv_path, sep=';', encoding='utf-8')
            except:
                try:
                    self.df = pd.read_csv(self.csv_path, sep=',', encoding='utf-8')
                except:
                    self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Strip whitespace from column names (CRITICAL for your CSV format)
            self.df.columns = self.df.columns.str.strip()
            
            # Also strip whitespace from all string values
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    self.df[col] = self.df[col].str.strip()
            
            print(f"📋 Columns found in CSV: {list(self.df.columns)}")
            
            # Parse dates from DD/MM/YYYY format
            self.df['date'] = pd.to_datetime(
                self.df['SEANCE'],
                format='%d/%m/%Y',
                errors='coerce'
            )
            
            # Rename columns to standardized format
            self.df = self.df.rename(columns={
                'CODE': 'stock_code',
                'VALEUR': 'stock_name',
                'OUVERTURE': 'open',
                'CLOTURE': 'close',
                'PLUS_BAS': 'low',
                'PLUS_HAUT': 'high',
                'QUANTITE_NEGOCIEE': 'volume',
                'NB_TRANSACTION': 'num_transactions',
                'CAPITAUX': 'capital_traded'
            })
            
            # Convert numeric columns
            numeric_cols = ['open', 'close', 'low', 'high', 'volume', 'num_transactions', 'capital_traded']
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            
            # Sort by date
            self.df = self.df.sort_values(['stock_code', 'date']).reset_index(drop=True)
            
            # Build stock metadata (for quick lookups)
            self._build_metadata()
            
            print(f"✅ Loaded {len(self.df):,} rows from {self.csv_path}")
            print(f"✅ Found {len(self.stock_metadata)} unique stocks")
            print(f"✅ Date range: {self.df['date'].min()} to {self.df['date'].max()}")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
    
    def _build_metadata(self):
        """Build metadata for each stock (total volume, trading days, etc.)"""
        for stock_code in self.df['stock_code'].unique():
            stock_df = self.df[self.df['stock_code'] == stock_code]
            
            self.stock_metadata[stock_code] = {
                'stock_name': stock_df['stock_name'].iloc[0],
                'total_volume': stock_df['volume'].sum(),
                'avg_daily_volume': stock_df['volume'].mean(),
                'trading_days': len(stock_df),
                'first_date': stock_df['date'].min(),
                'last_date': stock_df['date'].max(),
                'avg_price': stock_df['close'].mean()
            }
    
    def get_stock_data(
        self,
        stock_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        remove_zero_volume: bool = True
    ) -> pd.DataFrame:
        """
        Get historical data for a specific stock.
        
        Args:
            stock_code: ISIN code (e.g., 'TN0001600154')
            start_date: Start date in 'YYYY-MM-DD' format (optional)
            end_date: End date in 'YYYY-MM-DD' format (optional)
            remove_zero_volume: Remove days with zero trading volume
            
        Returns:
            DataFrame with columns: date, open, close, high, low, volume, num_transactions
        """
        # Filter by stock code
        stock_df = self.df[self.df['stock_code'] == stock_code].copy()
        
        if len(stock_df) == 0:
            raise ValueError(f"Stock code '{stock_code}' not found in dataset")
        
        # Filter by date range
        if start_date:
            start_date = pd.to_datetime(start_date)
            stock_df = stock_df[stock_df['date'] >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            stock_df = stock_df[stock_df['date'] <= end_date]
        
        # Remove zero-volume days if requested
        if remove_zero_volume:
            stock_df = stock_df[stock_df['volume'] > 0]
        
        # Select and order columns
        columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'num_transactions']
        stock_df = stock_df[columns].reset_index(drop=True)
        
        return stock_df
    
    def get_top_liquid_stocks(self, top_n: int = 10) -> List[dict]:
        """
        Get the most liquid stocks by average daily volume.
        
        Args:
            top_n: Number of top stocks to return
            
        Returns:
            List of dicts with stock_code, stock_name, avg_daily_volume, trading_days
        """
        # Sort stocks by average daily volume
        sorted_stocks = sorted(
            self.stock_metadata.items(),
            key=lambda x: x[1]['avg_daily_volume'],
            reverse=True
        )
        
        top_stocks = []
        for stock_code, metadata in sorted_stocks[:top_n]:
            top_stocks.append({
                'stock_code': stock_code,
                'stock_name': metadata['stock_name'],
                'avg_daily_volume': metadata['avg_daily_volume'],
                'trading_days': metadata['trading_days'],
                'avg_price': metadata['avg_price']
            })
        
        return top_stocks
    
    def get_stock_name(self, stock_code: str) -> str:
        """Get the company name for a given stock code."""
        if stock_code in self.stock_metadata:
            return self.stock_metadata[stock_code]['stock_name']
        return None
    
    def get_all_stock_codes(self) -> List[str]:
        """Get list of all available stock codes."""
        return list(self.stock_metadata.keys())
    
    def print_summary(self):
        """Print a summary of the dataset."""
        print("\n" + "="*60)
        print("BVMT DATASET SUMMARY")
        print("="*60)
        print(f"Total rows: {len(self.df):,}")
        print(f"Unique stocks: {len(self.stock_metadata)}")
        print(f"Date range: {self.df['date'].min().strftime('%Y-%m-%d')} to {self.df['date'].max().strftime('%Y-%m-%d')}")
        print(f"Total volume traded: {self.df['volume'].sum():,.0f}")
        print("\nTop 10 Most Liquid Stocks:")
        print("-"*60)
        
        top_stocks = self.get_top_liquid_stocks(10)
        for i, stock in enumerate(top_stocks, 1):
            print(f"{i:2d}. {stock['stock_name'][:30]:30s} | Avg Vol: {stock['avg_daily_volume']:>12,.0f}")
        
        print("="*60 + "\n")


# Convenience function for quick access
def get_stock_data(stock_code: str, csv_path: str = 'web_histo_cotation_2022.csv',
                   start_date: Optional[str] = None, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Quick function to load stock data without instantiating the class.
    
    Args:
        stock_code: ISIN code
        csv_path: Path to CSV file
        start_date: Start date in 'YYYY-MM-DD' format
        end_date: End date in 'YYYY-MM-DD' format
        
    Returns:
        DataFrame with historical stock data
    """
    loader = BVMTDataLoader(csv_path)
    return loader.get_stock_data(stock_code, start_date, end_date)


if __name__ == "__main__":
    # Test the data loader
    print("Testing BVMT Data Loader...")
    
    try:
        loader = BVMTDataLoader()
        loader.print_summary()
        
        # Test getting data for a stock
        top_stocks = loader.get_top_liquid_stocks(3)
        if top_stocks:
            test_code = top_stocks[0]['stock_code']
            print(f"\nTesting get_stock_data() for {test_code}...")
            df = loader.get_stock_data(test_code)
            print(df.head())
            print(f"\nShape: {df.shape}")
            
    except FileNotFoundError:
        print("⚠️  CSV file not found. Please ensure 'web_histo_cotation_2022.csv' is in the current directory.")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
