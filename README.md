# LLM Text Assistant

Projeto simples em Python para testar a integração de aplicações com modelos de linguagem (LLMs) por API.

A ideia foi criar um assistente de terminal que recebe um texto e permite escolher entre três tarefas: **resumir**, **explicar** ou **revisar a escrita**. É um projeto pequeno, mas útil para praticar chamadas de API, organização de prompts, variáveis de ambiente e tratamento de erros.

## Tecnologias

- Python 3.10+
- OpenAI API
- python-dotenv
- pytest (testes)

## Como executar

1. Clone o repositório e entre na pasta:

   ```bash
   git clone https://github.com/Dzelmee/llm-text-assistant.git
   cd llm-text-assistant
   ```

2. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux/macOS: source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Copie `.env.example` para `.env` e adicione sua chave da API:

   ```env
   OPENAI_API_KEY=sua_chave_aqui
   OPENAI_MODEL=gpt-4o-mini
   ```

4. Execute:

   ```bash
   python app.py
   ```

A API pode gerar custos conforme o modelo e o uso. **Nunca publique o arquivo `.env` ou sua chave de API.**

## Exemplo de uso

```text
LLM Text Assistant
1 - Resumir
2 - Explicar
3 - Revisar escrita
Escolha uma opção: 1
Cole seu texto. Para finalizar, digite FIM em uma linha separada:
Uma API permite a comunicação entre aplicações diferentes.
FIM

Resultado:
[resumo gerado pelo modelo]
```

## Testes

```bash
pytest -q
```

Os testes verificam a montagem das mensagens e as validações locais, sem consumir a API.

## O que pratiquei

- Integração com um LLM usando SDK e API
- Construção de prompts para tarefas diferentes
- Separação de configurações com variáveis de ambiente
- Tratamento básico de erros e testes unitários

## Próximos passos

Adicionar uma interface web e permitir salvar o histórico das interações.

---

Desenvolvido por [Jonas Dzelme](https://github.com/Dzelmee).
