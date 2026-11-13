"""Integração com provedores de modelos de linguagem."""
import os
from openai import OpenAI, NotFoundError
import logging

logger = logging.getLogger(__name__)
GROQ_DEFAULT_MODEL = "openai/gpt-oss-20b"
GROQ_FALLBACK_MODEL = "openai/gpt-oss-120b"
from app import build_messages

MAX_CHARS = 4000


def generate_text(task: str, text: str, provider: str = "groq", *, client=None, summary_length: str = "Médio") -> str:
    if len(text) > MAX_CHARS:
        raise ValueError(f"O limite é de {MAX_CHARS} caracteres por texto.")
    messages = build_messages(task, text, summary_length=summary_length)
    if provider == "groq":
        key = os.getenv("GROQ_API_KEY", "").strip()
        model = os.getenv("GROQ_MODEL", "").strip() or GROQ_DEFAULT_MODEL
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
    # GPT-OSS usa parte do orçamento para raciocínio antes de gerar a resposta.
    # Um limite de 650 tokens pode encerrar a geração antes do conteúdo visível.
    token_budget = 2048 if provider == "groq" else 650

    def request(selected_model: str, budget: int):
        return client.chat.completions.create(
            model=selected_model,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=budget,
        )

    try:
        response = request(model, token_budget)
    except NotFoundError:
        if provider != "groq" or model == GROQ_FALLBACK_MODEL:
            raise
        logger.warning("Modelo Groq indisponível (%s); tentando modelo alternativo", model)
        model = GROQ_FALLBACK_MODEL
        response = request(model, token_budget)

    choice = response.choices[0]
    result = choice.message.content
    if (not result or not result.strip()) and provider == "groq" and choice.finish_reason == "length":
        logger.warning("Geração Groq atingiu o limite de tokens sem resposta visível; tentando orçamento maior")
        response = request(model, 4096)
        result = response.choices[0].message.content

    if not result or not result.strip():
        raise ValueError("O modelo não retornou um texto. Tente novamente.")
    return result.strip()
