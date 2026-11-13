# LLM Text Assistant

Criei este projeto para praticar a integração de uma aplicação Python com um modelo de linguagem (LLM) por API.

O assistente recebe um texto e executa três tarefas: **resumir**, **explicar** ou **revisar a escrita**. Comecei com uma versão de terminal e depois adicionei uma interface web com Streamlit para facilitar os testes.

## Tecnologias

Python 3.10+ · OpenAI API · Streamlit · python-dotenv · pytest

## Dois modos de uso

- **Demonstração gratuita:** apresenta três exemplos fixos (resumo, explicação e revisão), sem chave e sem chamadas à API. Não processa textos personalizados nem usa IA; é uma prévia da experiência.
- **OpenAI API:** processa o texto digitado usando um modelo real. Precisa de chave no `.env` e créditos disponíveis. A API pode gerar custos.

## Funcionalidades

- Resumo de textos com foco nas informações principais
- Explicação de conteúdos em linguagem simples
- Revisão de escrita mantendo o sentido original
- Histórico de resultados durante a sessão da interface web
- Validação de entrada e tratamento básico de erros

## Como executar

Clone o projeto:

```bash
git clone https://github.com/Dzelmee/llm-text-assistant.git
cd llm-text-assistant
```

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate
pip install -r requirements.txt
```

Para testar **somente a demonstração**, não é necessário configurar chave nenhuma. Para usar o modo **OpenAI API**, copie `.env.example` para `.env` e configure sua chave:

```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
```

**Interface web:**

```bash
streamlit run web_app.py
```

O navegador abrirá a aplicação localmente, geralmente em `http://localhost:8501`.

**Versão de terminal:**

```bash
python app.py
```

## Testes

```bash
python -m pytest -q
```

Os testes unitários não fazem chamadas à API.

## Observações

- A chave da API fica no arquivo `.env`, que não é enviado ao GitHub.
- As chamadas à OpenAI podem gerar custos, dependendo do uso.
- O histórico da interface web fica apenas na sessão do navegador; não existe banco de dados.
- Não há versão hospedada: execute o projeto localmente. O modo demonstração funciona sem chave.
- As respostas do modo demonstração são exemplos estáticos e não devem ser apresentadas como resultados reais da API.

## O que aprendi

Pratiquei integração com APIs de LLMs, construção de prompts, organização de código Python, configuração por variáveis de ambiente, testes e desenvolvimento de uma interface simples.

## Próximos passos

Validar a integração real com créditos disponíveis, melhorar a experiência de uso e explorar outras opções de modelos.

---

Desenvolvido por [Jonas Dzelme](https://github.com/Dzelmee).
