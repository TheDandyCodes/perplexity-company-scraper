

# Perplexity Company Scraper

This project extracts structured information about Spanish companies using the Perplexity AI API. The main workflow reads company names from a CSV file and queries the API to obtain relevant data, saving the results in JSON format.

## Features

- Flexible configuration via `config.toml`.
- Customizable prompts per model in `prompts.yaml`.
- Data extraction with JSON schema validation.
- Modern dependency management with [uv](https://github.com/astral-sh/uv).
- Modular scripts: `ppl_scrapper.py` (main), `utils.py` (utilities).
- Support for logging and debug mode.

## Project Structure

```
perplexity-company-scraper/
├── README.md
├── config.toml
├── ppl_scrapper.py
├── prompts.yaml
├── utils.py
├── pyproject.toml
├── uv.lock
├── data/
│   ├── input/
│   │   └── companies.csv
│   └── output/
│       └── results.json
├── notebooks/
│   └── playground.ipynb
└── __pycache__/
```

## Installation & Dependencies

This project uses [uv](https://github.com/astral-sh/uv) for dependency management (faster and safer than pip).

1. Clone the repository:
   ```bash
   git clone https://github.com/TheDandyCodes/perplexity-company-scraper.git
   cd perplexity-company-scraper
   ```

2. Install uv (if you don't have it):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

## Configuration

### 1. Environment Variables

Create a `.env` file in the root and add your API key:
```
PERPLEXITY_API_KEY=your_perplexity_api_key
```

### 2. Configuration file (`config.toml`)

Example:
```toml
[data]
input_csv_path = "data/input/companies.csv"   # Path to input CSV
target_column = "Cuenta"                      # Column with company name

[model]
model_name = "sonar-pro"                      # Perplexity model to use
temperature = 0.1

[output]
output_csv_path = "data/output/results.json"  # Output path

[debug]
debug_mode = false
```

### 3. Customizable prompts (`prompts.yaml`)

Define prompts for each model and the expected response format. You can adapt the messages for each model as needed.

## Usage

1. Make sure your API key is in `.env` and your configuration is correct in `config.toml`.
2. Place your companies CSV file in `data/input/companies.csv` (or the path you define).
3. Run the main script:
   ```bash
   python ppl_scrapper.py
   ```

The script will process the companies, query the API, and save the results in `data/output/results.json`.

## Output

The output file is a CSV with structured data for each company, including the fields required by the JSON schema:

- `Cuenta`: Original company name
- `CIF`, `Razón Social`, `Teléfono`, `Sitio Web`, `CNAE`, `Descripción de CNAE`, `Sector`, `Número de Empleados min`, `Número de Empleados max`, `Ingresos anuales min`, `Ingresos anuales max`, `Pais`, `Estado/Provincia`, `Ciudad`, `Direccion`

## Main Scripts

- `ppl_scrapper.py`: Main script that loads data, queries the API, and saves results.
- `utils.py`: Helper functions for loading prompts and other utilities.

## Advanced Notes

- You can modify prompts in `prompts.yaml` to adapt model behavior.
- The script uses the column defined in `target_column` to look up the company name.
- Debug mode shows the cost of each query if `debug_mode = true` in `config.toml`.

## Updating Dependencies

To install new dependencies or update existing ones:

```bash
uv add <package>
uv sync
```

This will automatically update `pyproject.toml` and `uv.lock`.