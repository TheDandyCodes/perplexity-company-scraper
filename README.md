


# Perplexity Company Scraper

This project extracts structured information about Spanish companies using generative APIs (such as Perplexity and Gemini) and the **Chain of Responsibility** design pattern for flexible model management and error handling.

## Main Features

- Data extraction using a configurable chain of models (Chain of Responsibility).
- Flexible configuration via `config.toml`.
- Customizable prompts per model in `prompts.yaml`.
- Data validation with JSON schema.
- Modern dependency management with [uv](https://github.com/astral-sh/uv).
- Modular scripts: `main.py` (main), `cor_generative_extraction.py` (handlers and COR logic), `utils.py` (utilities).
- Support for logging and debug mode.

## Project Structure

```
perplexity-company-scraper/
├── README.md
├── config.toml
├── main.py
├── cor_generative_extraction.py
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

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

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
target_column = "Cuenta"                      # Column with the company name

[model]
model_name = "sonar-pro"                      # Perplexity model to use
temperature = 0.1

[chain_of_responsability]
model_chain = ["gemini", "perplexity", "fallback"] # Order of handlers

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
   python main.py
   ```

The script will process the companies, query the models in the order defined by the chain of responsibility, and save the results in the output file.

## Chain of Responsibility: How does it work?

The main flow (`main.py`) builds a chain of handlers (Gemini, Perplexity, Fallback) according to the configuration. Each handler tries to extract the company data:

- If the first model fails, the next one automatically takes over.
- The `Fallback` handler ensures a response is always returned, even if it's an error.
- You can modify the order and models in the `[chain_of_responsability]` section of `config.toml`.

## Output

The output file is a CSV with structured data for each company, including the fields required by the JSON schema:

- `Cuenta`: Original company name
- `CIF`, `Razón Social`, `Teléfono`, `Sitio Web`, `CNAE`, `Descripción de CNAE`, `Sector`, `Número de Empleados min`, `Número de Empleados max`, `Ingresos anuales min`, `Ingresos anuales max`, `Pais`, `Estado/Provincia`, `Ciudad`, `Direccion`, `request_cost`

## Main Scripts

- `main.py`: Main script that loads data, builds the chain of handlers, and saves results.
- `cor_generative_extraction.py`: Implements the handlers and the Chain of Responsibility logic.
- `utils.py`: Helper functions for loading prompts and utilities.

## Advanced Notes

- You can modify the prompts in `prompts.yaml` to adapt model behavior.
- The script uses the column defined in `target_column` to look up the company name.
- Debug mode shows the cost of each query if `debug_mode = true` in `config.toml`.

## Updating Dependencies

To install new dependencies or update existing ones:

```bash
uv add <package>
uv sync
```

This will automatically update `pyproject.toml` and `uv.lock`.