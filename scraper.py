#!/usr/bin/env python3
"""
Perplexity Company Scraper

This script reads a CSV file path from config.toml and makes structured API calls 
to Perplexity for each value in a specified column of the dataframe.
"""

import os
import json
import logging
import pandas as pd
import requests
import toml
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict, Any, List


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerplexityAPI:
    """Wrapper for Perplexity API calls."""
    
    def __init__(self, api_key: str, model: str = "llama-3.1-sonar-small-128k-online"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def query_company_info(self, company_name: str, max_tokens: int = 1000, temperature: float = 0.1) -> Dict[str, Any]:
        """
        Query Perplexity API for structured company information.
        
        Args:
            company_name: Name of the company to query
            max_tokens: Maximum tokens for the response
            temperature: Temperature for the response
            
        Returns:
            Structured company information
        """
        prompt = f"""
        Provide structured information about the company "{company_name}" in JSON format.
        Include the following fields if available:
        - company_name: Official company name
        - industry: Primary industry sector
        - headquarters: Location of headquarters
        - founded_year: Year the company was founded
        - employee_count: Approximate number of employees
        - revenue: Annual revenue (if public)
        - description: Brief company description
        - website: Official website URL
        
        If information is not available, use null for that field.
        Return only valid JSON without any additional text.
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides structured company information in JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from the response
            try:
                structured_data = json.loads(content)
                return {
                    "success": True,
                    "data": structured_data,
                    "raw_response": content
                }
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON for {company_name}. Raw response: {content}")
                return {
                    "success": False,
                    "error": "JSON parsing failed",
                    "raw_response": content
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed for {company_name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "raw_response": None
            }


class CompanyScraper:
    """Main class for processing CSV files and querying company information."""
    
    def __init__(self, config_path: str = "config.toml"):
        """Initialize the scraper with configuration."""
        self.config = self.load_config(config_path)
        self.api = self.setup_api()
        
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from TOML file."""
        try:
            with open(config_path, 'r') as f:
                config = toml.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file {config_path} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            raise
    
    def setup_api(self) -> PerplexityAPI:
        """Setup Perplexity API with credentials from environment."""
        load_dotenv()
        api_key = os.getenv("PERPLEXITY_API_KEY")
        
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
        
        model = self.config.get("api", {}).get("model", "llama-3.1-sonar-small-128k-online")
        return PerplexityAPI(api_key, model)
    
    def load_csv(self, csv_path: str) -> pd.DataFrame:
        """Load CSV file into a pandas DataFrame."""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows from {csv_path}")
            return df
        except FileNotFoundError:
            logger.error(f"CSV file {csv_path} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise
    
    def process_companies(self) -> List[Dict[str, Any]]:
        """Process all companies in the CSV file."""
        csv_path = self.config["data"]["csv_path"]
        target_column = self.config["data"]["target_column"]
        
        # Load the CSV
        df = self.load_csv(csv_path)
        
        if target_column not in df.columns:
            raise ValueError(f"Column '{target_column}' not found in CSV. Available columns: {list(df.columns)}")
        
        results = []
        
        # Get API configuration
        api_config = self.config.get("api", {})
        max_tokens = api_config.get("max_tokens", 1000)
        temperature = api_config.get("temperature", 0.1)
        
        for index, row in df.iterrows():
            company_name = row[target_column]
            
            if pd.isna(company_name) or not company_name.strip():
                logger.warning(f"Skipping empty company name at row {index}")
                continue
            
            logger.info(f"Processing company {index + 1}/{len(df)}: {company_name}")
            
            # Query API for company information
            api_result = self.api.query_company_info(
                company_name, 
                max_tokens=max_tokens, 
                temperature=temperature
            )
            
            # Combine with original row data
            result = {
                "row_index": index,
                "original_data": row.to_dict(),
                "api_result": api_result,
                "timestamp": pd.Timestamp.now().isoformat()
            }
            
            results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]]) -> None:
        """Save results to output file."""
        output_path = self.config.get("output", {}).get("output_path", "output/results.json")
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_path}")
    
    def run(self) -> None:
        """Run the complete scraping process."""
        logger.info("Starting company scraping process")
        
        try:
            results = self.process_companies()
            self.save_results(results)
            
            # Print summary
            successful_queries = sum(1 for r in results if r["api_result"]["success"])
            total_queries = len(results)
            
            logger.info(f"Scraping completed successfully!")
            logger.info(f"Processed {total_queries} companies")
            logger.info(f"Successful API queries: {successful_queries}/{total_queries}")
            
        except Exception as e:
            logger.error(f"Scraping process failed: {str(e)}")
            raise


def main():
    """Main entry point."""
    try:
        scraper = CompanyScraper()
        scraper.run()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()