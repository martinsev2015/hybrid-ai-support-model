import re
import requests
from src.config import EMOJI_API_KEY

EMOJI_PATTERN = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF]")

_emoji_db_cache = None

def _get_emoji_db():
    global _emoji_db_cache
    if _emoji_db_cache is None:
        url = f"https://emoji-api.com/emojis?access_key={EMOJI_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        _emoji_db_cache = response.json()
    return _emoji_db_cache

# Mant\u00E9m compatibilidade com c\u00F3digo que importa EMOJI_DB diretamente
class _LazyEmojiDB(list):
    def __iter__(self):
        return iter(_get_emoji_db())
    def __len__(self):
        return len(_get_emoji_db())

EMOJI_DB = _LazyEmojiDB()

def extrair_emojis(texto):
    return EMOJI_PATTERN.findall(texto)

def contem_apenas_emoji(texto):
    texto = texto.strip()
    if not texto:
        return True

    texto_sem_emoji = re.sub(EMOJI_PATTERN, "", texto)
    return texto_sem_emoji.strip() == ""
