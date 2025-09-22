import yaml


def load_prompts(yaml_path: str) -> dict:
    """Load prompts from a YAML file for a specific model.

    Parameters
    ----------
    yaml_path : str
        Path to the YAML file containing prompts.

    Returns
    -------
    dict
        A dictionary containing the prompts.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data
