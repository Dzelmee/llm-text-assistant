# LLM Text Assistant

Criei este projeto para praticar a integração de uma aplicação Python com um modelo de linguagem (LLM) por API.

O assistente recebe um texto e executa três tarefas: **resumir**, **explicar** ou **revisar a escrita**. Comecei com uma versão de terminal e depois adicionei uma interface web com Streamlit para facilitar os testes.

## Tecnologias

Python 3.10+ · OpenAI API · Streamlit · python-dotenv · pytest

## Acesso público e integração gratuita

O aplicativo também pode ser publicado no Streamlit Community Cloud. Para permitir textos personalizados sem exigir conta dos visitantes, ele usa a API Groq com um modelo open-source. A modalidade gratuita possui cotas; quando elas acabam, o site informa a indisponibilidade em vez de cobrar ou trocar para um provedor pago.

### Configurar Groq

1. Crie uma chave em https://console.groq.com/keys (não a publique).
2. Localmente, adicione `GROQ_API_KEY` ao arquivo `.env`.
3. No Streamlit Community Cloud, selecione este repositório, branch `main`, arquivo `web_app.py`.
4. Em **Advanced settings → Secrets**, informe:

```toml
GROQ_API_KEY = "sua_chave_groq"
GROQ_MODEL = "llama-3.1-8b-instant"
```

5. Faça o deploy e teste com um texto próprio.

Os visitantes não precisam criar conta ou instalar nada. O limite por texto é de 4.000 caracteres, com intervalo mínimo de 15 segundos e até 15 solicitações por sessão. Esses controles por sessão **não impedem abuso distribuído**; para tráfego maior, será necessário rate limiting persistente no servidor e monitoramento das cotas.

Evite inserir dados sensíveis: os textos são enviados ao provedor de IA para processamento. O site não mantém histórico em banco de dados.

## Dois modos de uso

- **IA gratuita (Groq):** processa textos próprios usando o provedor Groq, sujeito a cotas do serviço.\n- **Demonstração gratuita:** apresenta três exemplos fixos (resumo, explicação e revisão), sem chave e sem chamadas à API. Não processa textos personalizados nem usa IA; é uma prévia da experiência.
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

Para testar **somente a demonstração**, não é necessário configurar chave nenhuma. Para testar o modo Groq localmente, adicione `GROQ_API_KEY` ao `.env`. Para usar o modo **OpenAI API**, copie `.env.example` para `.env` e configure sua chave:

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
- O deploy público deve ser feito no Streamlit Community Cloud, com a chave armazenada em Secrets. Sem configurar a chave Groq, o modo gratuito não funcionará.
- As respostas do modo demonstração são exemplos estáticos e não devem ser apresentadas como resultados reais da API.

## O que aprendi

Pratiquei integração com APIs de LLMs, construção de prompts, organização de código Python, configuração por variáveis de ambiente, testes e desenvolvimento de uma interface simples.

## Próximos passos

Validar a integração real com créditos disponíveis, melhorar a experiência de uso e explorar outras opções de modelos.

---

Desenvolvido por [Jonas Dzelme](https://github.com/Dzelmee).
