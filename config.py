import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
EMOJI_API_KEY = os.getenv("EMOJI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError("Defina OPENAI_API_KEY no .env")
if not OPENAI_MODEL:
    raise RuntimeError("Defina OPENAI_MODEL no .env")
if not EMOJI_API_KEY:
    raise RuntimeError("Defina EMOJI_API_KEY no .env")

client = OpenAI(api_key=OPENAI_API_KEY)