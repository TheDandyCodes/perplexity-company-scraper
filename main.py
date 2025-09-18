from cor_generative_extraction import GeminiHandler, PerplexityHandler, FallbackHandler
from dotenv import load_dotenv
import toml
from utils import load_prompts
import pandas as pd
import random
import time
load_dotenv()
CONFIG = toml.load("config.toml")
PROMPTS = load_prompts("prompts.yaml")

HANDLER_MAPPING = {
    "gemini": GeminiHandler,
    "perplexity": PerplexityHandler,
    "fallback": FallbackHandler,
}

def build_chain_from_config():
    """Read the config and build the chain of handlers."""
    
    try: 
        model_chain = CONFIG["chain_of_responsability"]["model_chain"]
    except KeyError:
        raise ValueError("Configuration for chain_of_responsability is missing or incomplete.")

    # Instance first handler
    first_handler = HANDLER_MAPPING[model_chain[0]]()
    current_handler = first_handler

    # Instantiate and link following handlers
    for model_name in model_chain[1:]:
        next_handler = HANDLER_MAPPING[model_name]()
        current_handler.set_next(next_handler)
        current_handler = next_handler
        
    return first_handler


if __name__ == "__main__":
    chain_head = build_chain_from_config()
    
    companies_df = pd.read_csv(CONFIG["data"]["input_csv_path"])

    required_cols = [col for col in companies_df.columns if col != "Cuenta"]

    completed_jsonl = []
    list_of_costs = []
    for idx, row in companies_df.iterrows():

        print(f"\n--- Procesando: {row['Cuenta']} ---")
        result = chain_head.handle(row["Cuenta"])
        # Process range fields
        for range_col in ["Número de Empleados", "Ingresos anuales"]:
            if result.get(range_col, None) is not None and isinstance(result[range_col], list):
                if len(result[range_col]) > 1:
                    result[f"{range_col} min"] = result[range_col][0]
                    result[f"{range_col} max"] = result[range_col][-1]
                elif len(result[range_col]) == 1:
                    result[f"{range_col} min"] = result[range_col][0]
                    result[f"{range_col} max"] = result[range_col][0]

        jsonl = {
            "Cuenta": row["Cuenta"],
            **result,
        }
        completed_jsonl.append(jsonl)
        print("--------------------------")
        # Add a random sleep time between 1.5 and 2.5 seconds to avoid rate limiting
        sleep_time = 1.5 + random.uniform(0.3, 1.0)
        time.sleep(sleep_time)

    # Save the new dataframe in output_path
    completed_df = pd.DataFrame(completed_jsonl)
    print(f"\033[91mTotal cost: {completed_df['request_cost'].sum()} $\033[0m")
    completed_df.to_csv(CONFIG["output"]["output_csv_path"], index=False)