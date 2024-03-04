"""
config.py
"""
import os

from pydantic import BaseModel

# Constants
GPT3 = "gpt-35-turbo-16k"
GPT4 = "gpt-4-32k"

# Input data model for the fastapi endpoints
class JDRequest(BaseModel):
    """
    Pydantic model for the request payload of the /simplify-text endpoint.
    It expects two fields:
    - text: A string representing the text to be simplified.
    - language: A string that must be either 'english' or 'chinese'.
    """
    job_title: str
    job_description: str

# API Key
API_KEY = os.getenv("API_KEY")

# Azure OpenAI API Configuration
AZURE_API_KEY = os.getenv("JODIE_API_KEY")
AZURE_API_VER = "2024-02-15-preview"
AZURE_ENDPOINT = os.getenv("JODIE_ENDPOINT")
