# Chain of Responsibility (COR) Pattern for Generative Extraction

# Enables use type hints of the class itself within the class definition
from __future__ import annotations

import json
import os
import random
from abc import ABC, abstractmethod
from typing import Any, Optional

import requests
import toml
from dotenv import load_dotenv

from utils import load_prompts

load_dotenv()
CONFIG = toml.load("config.toml")
PROMPTS = load_prompts("prompts.yaml")


class Handler(ABC):
    """Interface for handling requests in the chain of responsibility."""

    @abstractmethod
    def set_next(self, handler: Handler) -> Handler:
        pass

    @abstractmethod
    def handle(self, request) -> dict:
        pass


class GenerativeModelHandler(Handler):
    """
    Handler class for processing requests using a generative model.
    """

    _next_handler: Optional[Handler] = None

    def set_next(self, handler: Handler) -> Handler:
        self._next_handler = handler
        # Returning a handler from here will let us link handlers in a
        # convenient way like this:
        # link1.set_next(link2).set_next(link3)
        return handler

    @abstractmethod
    def handle(self, request: Any) -> dict:
        if self._next_handler:
            return self._next_handler.handle(request)

        return {}


class GeminiHandler(GenerativeModelHandler):
    def handle(self, request: str) -> dict:
        print(f"-> Intentando con Gemini para '{request}'...")
        try:
            # --- This is where the actual logic of the Gemini API would go. ---
            # We simulate a possible failure
            if "error" in request.lower() or random.random() < 0.5:
                raise ValueError("Gemini could not process the request.")

            # If successful
            # Simulated successful response
            result = {
                "CIF": "A15075062",
                "Razón Social": "INDUSTRIA DE DISEÑO TEXTIL, S.L.",
                "Teléfono": "+34981185400",
                "Sitio Web": "https://www.compañia.com/",
                "CNAE": "4771",
                "Descripción de CNAE": "Comercio al por menor de prendas de vestir en establecimientos especializados",
                "Sector": "Comercio Minorista",
                "Número de Empleados": [0, 10],
                "Ingresos anuales": [300000000, 3500000000],
                "Pais": "España",
                "Estado/Provincia": "A Coruña",
                "Ciudad": "Arteixo",
                "Direccion": "Avenida de la Diputacion, Edificio Compañía, 15142",
                "request_cost": round(random.uniform(0.5, 2.0), 4),
            }
            print("Success with Gemini!")
            return result

        except Exception as e:
            print(f"Failure in Gemini: {e}. Passing to the next.")
            # If it fails, pass the request to the next in the chain
            return super().handle(request)


class PerplexityHandler(GenerativeModelHandler):
    def handle(self, request: Any) -> dict:
        print(f"-> Intentando con Perplexity para '{request}'...")
        try:
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
                    "Número de Empleados": {
                        "type": "array",
                        "items": {"type": "integer"},
                    },
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
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {os.getenv('PERPLEXITY_API_KEY')}",
                "Content-Type": "application/json",
            }
            data = {
                "model": CONFIG["model"]["model_name"],
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "system",
                        "content": PROMPTS["models"][CONFIG["model"]["model_name"]][
                            "system"
                        ],
                    },
                    {
                        "role": "user",
                        "content": PROMPTS["models"][CONFIG["model"]["model_name"]][
                            "user"
                        ].format(company_name=request),
                    },
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {"schema": company_info_json_schema},
                },
            }
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            response_dict = response.json()
            company_info = json.loads(response_dict["choices"][0]["message"]["content"])
            company_info["request_cost"] = response_dict["usage"]["cost"]["total_cost"]
            return company_info

        except Exception as e:
            print(f"Failure in Perplexity: {e}. Passing to the next.")
            return super().handle(request)

class FallbackHandler(GenerativeModelHandler):
    """A final handler that captures everything the others couldn't."""
    def handle(self, request: str) -> dict:
        print(f"-> Fallback for '{request}'.")
        # This handler never fails, it just logs the final error.
        error_message = f"ERROR: No model could process '{request}'."
        print(error_message)
        error_dict = {
            "CIF": "Error",
            "Razón Social": "Error",
            "Teléfono": "Error",
            "Sitio Web": "Error",
            "CNAE": "Error",
            "Descripción de CNAE": "Error",
            "Sector": "Error",
            "Número de Empleados": [0, 0],
            "Ingresos anuales": [0, 0],
            "Pais": "Error",
            "Estado/Provincia": "Error",
            "Ciudad": "Error",
            "Direccion": "Error"
        }
        return error_dict

