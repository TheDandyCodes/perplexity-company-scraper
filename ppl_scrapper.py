# Adapted for company info extraction using ppl_scrapper.py logic
import json
import os

import pandas as pd
import requests
import toml
from dotenv import load_dotenv

from utils import load_prompts

CONFIG = toml.load("config.toml")
PROMPTS = load_prompts("prompts.yaml")

load_dotenv()


def create_perplexity_company_request(api_key, prompt, json_schema, model_name):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model_name,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": json_schema},
        },
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


# JSON schema for company info (matches CompanyInfoSchema from ppl_scrapper.py)
company_info_json_schema = {
    "type": "object",
    "properties": {
        "CIF": {"type": "string"},
        "Razón Social": {"type": "string"},
        "Teléfono": {"type": "string"},
        "Sitio Web": {"type": "string"},
        "CNAE": {"type": "string"},
        "Descripción de CNAE": {"type": "string"},
        "Sector": {"type": "string"},
        "Número de Empleados": {"type": "array", "items": {"type": "integer"}},
        "Ingresos anuales": {"type": "array", "items": {"type": "number"}},
        "Pais": {"type": "string"},
        "Estado/Provincia": {"type": "string"},
        "Ciudad": {"type": "string"},
        "Direccion": {"type": "string"},
    },
    "required": [
        "CIF",
        "Razón Social",
        "Teléfono",
        "Sitio Web",
        "CNAE",
        "Descripción de CNAE",
        "Sector",
        "Número de Empleados",
        "Ingresos anuales",
        "Pais",
        "Estado/Provincia",
        "Ciudad",
        "Direccion",
    ],
}

if __name__ == "__main__":
    companies_df = pd.read_csv(CONFIG["data"]["input_csv_path"])
    # Example: extract info for first company
    company_name = (
        companies_df.iloc[0]["Cuenta"]
        if "Cuenta" in companies_df.columns
        else "Bodegas Ramón Bilbao S.A."
    )
    prompt = PROMPTS["models"][CONFIG["model"]["model_name"]]["user"].format(
        company_name=company_name
    )
    response = create_perplexity_company_request(
        os.getenv("PERPLEXITY_API_KEY"),
        prompt,
        company_info_json_schema,
        CONFIG["model"]["model_name"],
    )
    print(response["choices"][0]["message"]["content"])
