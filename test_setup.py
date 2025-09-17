#!/usr/bin/env python3
"""
Test script to validate configuration and CSV loading without making API calls.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import CompanyScraper
import pandas as pd
import toml

def test_config_loading():
    """Test configuration loading."""
    print("Testing configuration loading...")
    try:
        with open("config.toml", 'r') as f:
            config = toml.load(f)
        print("✓ Configuration loaded successfully")
        print(f"  - CSV path: {config['data']['csv_path']}")
        print(f"  - Target column: {config['data']['target_column']}")
        print(f"  - Output path: {config['output']['output_path']}")
        return config
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return None

def test_csv_loading(config):
    """Test CSV loading."""
    print("\nTesting CSV loading...")
    try:
        csv_path = config['data']['csv_path']
        target_column = config['data']['target_column']
        
        df = pd.read_csv(csv_path)
        print(f"✓ CSV loaded successfully")
        print(f"  - Rows: {len(df)}")
        print(f"  - Columns: {list(df.columns)}")
        
        if target_column in df.columns:
            print(f"✓ Target column '{target_column}' found")
            print(f"  - Values: {df[target_column].tolist()}")
        else:
            print(f"✗ Target column '{target_column}' not found")
            
        return df
    except Exception as e:
        print(f"✗ CSV loading failed: {e}")
        return None

def main():
    """Main test function."""
    print("Running validation tests...\n")
    
    config = test_config_loading()
    if config is None:
        return False
        
    df = test_csv_loading(config)
    if df is None:
        return False
    
    print("\n✓ All validation tests passed!")
    print("The script is ready to run with a valid PERPLEXITY_API_KEY")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)