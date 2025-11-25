import os

from dotenv import load_dotenv

load_dotenv()

SECRET_ACCESS_TOKEN = os.getenv("SECRET_KEY")
SECRET_ALGORITHM = os.getenv("ALGORITHM")
OPENAI_TOKEN = os.getenv("OPENAI_API_TOKEN")
OPENAI_ENDPOINT = os.getenv("ENDPOINT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
GPT_MODEL = os.getenv("DEPLOYMENT")