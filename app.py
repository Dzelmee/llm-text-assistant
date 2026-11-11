"""Assistente simples de texto com um modelo de linguagem via API."""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

TASKS = {
    "1": "Resuma o texto em português, mantendo as informações principais.",
    "2": "Explique o texto de forma simples, em português, sem inventar informações.",
    "3": "Revise a escrita do texto em português, mantendo seu sentido e tom.",
}


def build_messages(task: str, text: str) -> list[dict[str, str]]:
    if task not in TASKS:
        raise ValueError("Opção inválida")
    if not text.strip():
        raise ValueError("O texto não pode estar vazio")
    return [
        {"role": "system", "content": "Você é um assistente de texto objetivo. Não invente fatos."},
        {"role": "user", "content": f"{TASKS[task]}\n\nTexto:\n{text.strip()}"},
    ]


def main() -> int:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("Configure OPENAI_API_KEY no arquivo .env antes de continuar.")
        return 1

    print("\nLLM Text Assistant")
    for key, label in (("1", "Resumir"), ("2", "Explicar"), ("3", "Revisar escrita")):
        print(f"{key} - {label}")
    task = input("Escolha uma opção: ").strip()
    if task not in TASKS:
        print("Opção inválida.")
        return 1

    print("Cole seu texto. Para finalizar, digite FIM em uma linha separada:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "FIM":
            break
        lines.append(line)

    try:
        messages = build_messages(task, "\n".join(lines))
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=messages,
            temperature=0.3,
        )
        print("\nResultado:\n")
        print(response.choices[0].message.content or "Nenhuma resposta retornada.")
        return 0
    except (ValueError, OpenAIError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
