from openai import AzureOpenAI
from src.constants.properties import OPENAI_TOKEN, OPENAI_ENDPOINT, OPENAI_API_VERSION

client = AzureOpenAI(
    api_key=OPENAI_TOKEN,
    azure_endpoint=OPENAI_ENDPOINT,
    api_version=OPENAI_API_VERSION
)
