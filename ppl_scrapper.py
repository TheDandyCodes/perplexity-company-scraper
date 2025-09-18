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


def create_perplexity_company_request(
    api_key, system_prompt, user_prompt, json_schema, model_name
) -> dict:
    """Create a request to the Perplexity API to obtain information about a company.

    Parameters
    ----------
    api_key : _type_
        Perplexity API key.
    prompt : _type_
        The prompt to send to the API.
    json_schema : _type_
        The JSON schema to validate the API response.
    model_name : _type_
        The name of the model to use for the API request.

    Returns
    -------
    dict
        The API response as a dictionary.
    """
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": model_name,
        "temperature": 0.1,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"schema": json_schema},
        },
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()


# JSON schema for company info
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
    import random
    import time

    from tqdm import tqdm

    companies_df = pd.read_csv(CONFIG["data"]["input_csv_path"]).head(2)
    target_col = CONFIG["target_column"]["col_name"]
    required_cols = list(company_info_json_schema["properties"].keys())

    completed_jsonl = []
    list_of_costs = []
    for idx, row in tqdm(companies_df.iterrows(), total=companies_df.shape[0]):
        missing = [
            col
            for col in required_cols
            if pd.isna(row.get(col, None)) or row.get(col, None) == ""
        ]
        if missing:
            prompt = PROMPTS["models"][CONFIG["model"]["model_name"]]["user"].format(
                company_name=row[target_col]
            )
            response = create_perplexity_company_request(
                os.getenv("PERPLEXITY_API_KEY"),
                PROMPTS["models"][CONFIG["model"]["model_name"]]["system"],
                PROMPTS["models"][CONFIG["model"]["model_name"]]["user"].format(
                    company_name=row[target_col]
                ),
                company_info_json_schema,
                CONFIG["model"]["model_name"],
            )
            # Print cost
            total_cost = response["usage"]["cost"]["total_cost"]
            list_of_costs.append(total_cost)
            # Print cost if in debug mode
            if CONFIG["debug"]["debug_mode"]:
                print("\n\033[92m{} $ used in this request\033[0m\n".format(total_cost))

            content = response["choices"][0]["message"]["content"]
            try:
                info = json.loads(content)

                # Process range fields
                for range_col in ["Número de Empleados", "Ingresos anuales"]:
                    if info.get(range_col, None) is not None and isinstance(
                        info[range_col], list
                    ):
                        if len(info[range_col]) > 1:
                            info[f"{range_col} min"] = info[range_col][0]
                            info[f"{range_col} max"] = info[range_col][-1]
                        elif len(info[range_col]) == 1:
                            info[f"{range_col} min"] = info[range_col][0]
                            info[f"{range_col} max"] = info[range_col][0]

                jsonl = {
                    target_col: row[target_col],
                    **info,
                }
                completed_jsonl.append(jsonl)
            except Exception as e:
                print(f"Error parsing response for row {idx}: {e}")
            # Sleep 1500ms + jitter >=300ms
            sleep_time = 1.5 + random.uniform(0.3, 1.0)
            time.sleep(sleep_time)

    # Save the new dataframe in output_path
    completed_df = pd.DataFrame(completed_jsonl)
    print(f"\033[91mTotal cost: {sum(list_of_costs)} $\033[0m")
    completed_df.to_csv(CONFIG["output"]["output_csv_path"], index=False)
