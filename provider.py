"""Integração com provedores de modelos de linguagem."""
import os
from openai import OpenAI
from app import build_messages

MAX_CHARS = 4000


def generate_text(task: str, text: str, provider: str = "groq", *, client=None) -> str:
    if len(text) > MAX_CHARS:
        raise ValueError(f"O limite é de {MAX_CHARS} caracteres por texto.")
    messages = build_messages(task, text)
    if provider == "groq":
        key = os.getenv("GROQ_API_KEY", "").strip()
        model = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
        url = "https://api.groq.com/openai/v1"
    elif provider == "openai":
        key = os.getenv("OPENAI_API_KEY", "").strip()
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        url = None
    else:
        raise ValueError("Provedor inválido.")
    if not key and client is None:
        raise ValueError("Serviço de IA ainda não configurado pelo responsável pelo site.")
    if client is None:
        client = OpenAI(api_key=key, base_url=url, timeout=30.0, max_retries=0)
    response = client.chat.completions.create(
        model=model, messages=messages, temperature=0.3, max_tokens=650
    )
    result = response.choices[0].message.content
    if not result or not result.strip():
        raise ValueError("O modelo não retornou um texto. Tente novamente.")
    return result.strip()
