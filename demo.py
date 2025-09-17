#!/usr/bin/env python3
"""
Demo script to show expected output format without requiring API key.
This creates mock API responses to demonstrate the scraper functionality.
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path

def create_mock_api_response(company_name: str) -> dict:
    """Create a mock API response for demonstration."""
    
    # Mock data for different companies
    mock_data = {
        "Apple Inc": {
            "company_name": "Apple Inc.",
            "industry": "Technology",
            "headquarters": "Cupertino, California, USA",
            "founded_year": 1976,
            "employee_count": "164,000+",
            "revenue": "$394.3 billion (2022)",
            "description": "Multinational technology company that designs and manufactures consumer electronics, software, and online services.",
            "website": "https://www.apple.com"
        },
        "Microsoft Corporation": {
            "company_name": "Microsoft Corporation",
            "industry": "Technology",
            "headquarters": "Redmond, Washington, USA",
            "founded_year": 1975,
            "employee_count": "221,000+",
            "revenue": "$198.3 billion (2022)",
            "description": "Multinational technology company that develops, licenses, and supports software, services, devices and solutions.",
            "website": "https://www.microsoft.com"
        },
        "Tesla Inc": {
            "company_name": "Tesla, Inc.",
            "industry": "Automotive/Clean Energy",
            "headquarters": "Austin, Texas, USA",
            "founded_year": 2003,
            "employee_count": "127,855",
            "revenue": "$81.5 billion (2022)",
            "description": "Electric vehicle and clean energy company that designs and manufactures electric cars, energy storage systems, and solar panels.",
            "website": "https://www.tesla.com"
        },
        "Amazon.com Inc": {
            "company_name": "Amazon.com, Inc.",
            "industry": "E-commerce/Cloud Computing",
            "headquarters": "Seattle, Washington, USA",
            "founded_year": 1994,
            "employee_count": "1,541,000+",
            "revenue": "$513.98 billion (2022)",
            "description": "Multinational technology company focusing on e-commerce, cloud computing, online advertising, digital streaming, and artificial intelligence.",
            "website": "https://www.amazon.com"
        },
        "Google LLC": {
            "company_name": "Google LLC",
            "industry": "Technology",
            "headquarters": "Mountain View, California, USA",
            "founded_year": 1998,
            "employee_count": "190,000+",
            "revenue": "$282.8 billion (2022)",
            "description": "Multinational technology company specializing in internet-related services and products including search engine, online advertising, cloud computing, and software.",
            "website": "https://www.google.com"
        }
    }
    
    return {
        "success": True,
        "data": mock_data.get(company_name, {
            "company_name": company_name,
            "industry": "Unknown",
            "headquarters": "Unknown",
            "founded_year": None,
            "employee_count": "Unknown",
            "revenue": "Unknown",
            "description": f"Information not available for {company_name}",
            "website": None
        }),
        "raw_response": f"Mock response for {company_name}"
    }

def run_demo():
    """Run the demonstration."""
    print("🚀 Perplexity Company Scraper - Demo Mode")
    print("=" * 50)
    
    # Load the CSV
    csv_path = "data/companies.csv"
    try:
        df = pd.read_csv(csv_path)
        print(f"📊 Loaded CSV: {len(df)} companies")
        print(f"   Columns: {list(df.columns)}")
        print()
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    # Create demo results
    results = []
    
    for index, row in df.iterrows():
        company_name = row['company_name']
        print(f"🔍 Processing: {company_name}")
        
        # Create mock API response
        api_result = create_mock_api_response(company_name)
        
        # Create result entry
        result = {
            "row_index": index,
            "original_data": row.to_dict(),
            "api_result": api_result,
            "timestamp": datetime.now().isoformat()
        }
        
        results.append(result)
        
        # Show summary of what was "found"
        if api_result["success"]:
            data = api_result["data"]
            print(f"   ✅ Found: {data.get('industry', 'Unknown')} company")
            print(f"      Founded: {data.get('founded_year', 'Unknown')}")
            print(f"      HQ: {data.get('headquarters', 'Unknown')}")
        else:
            print(f"   ❌ Failed to get data")
        print()
    
    # Save results
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / "demo_results.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Results saved to: {output_path}")
    print(f"📈 Processed {len(results)} companies successfully")
    
    # Show sample output structure
    print("\n📋 Sample Output Structure:")
    print("=" * 30)
    sample_result = results[0] if results else {}
    print(json.dumps(sample_result, indent=2)[:500] + "..." if len(json.dumps(sample_result, indent=2)) > 500 else json.dumps(sample_result, indent=2))
    
    return results

if __name__ == "__main__":
    results = run_demo()
    
    if results:
        print(f"\n🎉 Demo completed successfully!")
        print(f"   In production, set PERPLEXITY_API_KEY in .env and run: python scraper.py")
    else:
        print(f"\n❌ Demo failed")