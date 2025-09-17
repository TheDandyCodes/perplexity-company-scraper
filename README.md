# Perplexity Company Scraper

A Python script that reads company names from a CSV file and fetches structured company information using the Perplexity AI API.

## Features

- Reads CSV file path from `config.toml` configuration
- Makes structured API calls to Perplexity for each company in the dataset
- Returns structured JSON data with company information
- Configurable API parameters and output settings
- Comprehensive logging and error handling

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your Perplexity API key
   ```

4. Configure the script by editing `config.toml`:
   - Set the path to your CSV file
   - Specify which column contains company names
   - Adjust API parameters as needed

## Configuration

### config.toml
```toml
[data]
csv_path = "data/companies.csv"        # Path to your CSV file
target_column = "company_name"         # Column name to use for queries

[api]
model = "llama-3.1-sonar-small-128k-online"  # Perplexity model to use
max_tokens = 1000                      # Maximum response tokens
temperature = 0.1                      # Response temperature

[output]
output_path = "output/results.json"    # Where to save results
```

### .env
```
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

## Usage

1. Prepare your CSV file with company names
2. Update `config.toml` with the correct path and column name
3. Run the scraper:
   ```bash
   python scraper.py
   ```

The script will:
- Read the CSV file specified in the configuration
- Process each company name in the specified column
- Query Perplexity API for structured company information
- Save results to the output file in JSON format

## Output Format

The output JSON file contains an array of results, where each item includes:
- `row_index`: Original row number from CSV
- `original_data`: Complete original row data from CSV
- `api_result`: Structured company information from Perplexity
- `timestamp`: When the query was processed

Example output structure:
```json
[
  {
    "row_index": 0,
    "original_data": {
      "company_name": "Apple Inc",
      "location": "Cupertino CA",
      "sector": "Technology"
    },
    "api_result": {
      "success": true,
      "data": {
        "company_name": "Apple Inc.",
        "industry": "Technology",
        "headquarters": "Cupertino, California",
        "founded_year": 1976,
        "employee_count": "164,000+",
        "revenue": "$394.3 billion (2022)",
        "description": "Multinational technology company...",
        "website": "https://www.apple.com"
      }
    },
    "timestamp": "2024-01-01T12:00:00"
  }
]
```

## Error Handling

The script includes comprehensive error handling for:
- Missing configuration files
- Invalid CSV files or missing columns
- API request failures
- JSON parsing errors
- Network connectivity issues

All errors are logged with timestamps and detailed error messages.

## Requirements

- Python 3.7+
- Perplexity AI API key
- Internet connection for API calls

See `requirements.txt` for Python package dependencies.