# Texto. — Assistente de escrita

Aplicação web para resumir, explicar e revisar textos com modelos de linguagem. A proposta é oferecer uma ferramenta simples, acessível pelo navegador, com foco em clareza e experiência de uso.

**[Acessar o aplicativo](https://llm-text-assistant-dzelmee.streamlit.app/)** · **[Código-fonte](https://github.com/Dzelmee/llm-text-assistant)**

## Funcionalidades

- **Resumir:** destaca as informações essenciais de um texto.
- **Explicar:** apresenta conteúdos em uma linguagem mais simples.
- **Revisar:** melhora a escrita, preservando o sentido original.
- **Histórico temporário:** permite consultar os resultados durante a sessão.
- **Modo demonstração:** apresenta exemplos fixos sem consumir a API.

A interface utiliza uma paleta verde-sálvia, animações discretas em CSS e um mascote criado com elementos visuais da própria página.

## Tecnologias

- **Python:** lógica da aplicação e validação de entradas.
- **Streamlit:** interface web e gerenciamento da sessão.
- **GroqCloud + Llama:** processamento de textos com um modelo de linguagem.
- **OpenAI API:** provedor alternativo, opcional.
- **pytest:** testes automatizados.
- **GitHub Actions:** verificação de sintaxe e execução dos testes.
- **CSS:** identidade visual, responsividade e animações.

## Como funciona

O usuário escolhe uma ação, insere um texto e envia a solicitação. A aplicação valida a entrada, prepara as instruções e consulta o provedor configurado. O resultado é exibido na interface e mantido apenas durante a sessão.

O modo público utiliza a API Groq, sujeita aos limites do serviço gratuito. Quando a cota é atingida, a aplicação apresenta uma mensagem de indisponibilidade; não há troca automática para um serviço pago.

## Executar localmente

Requisitos: Python 3.10 ou superior.

```bash
git clone https://github.com/Dzelmee/llm-text-assistant.git
cd llm-text-assistant
python -m venv .venv
```

Ative o ambiente virtual:

```powershell
# Windows / PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instale as dependências e inicie a aplicação:

```bash
pip install -r requirements.txt
streamlit run web_app.py
```

Para utilizar a IA localmente, copie `.env.example` para `.env` e configure a variável `GROQ_API_KEY`. O modo demonstração funciona sem chave.

## Publicação no Streamlit Community Cloud

Utilize o repositório `Dzelmee/llm-text-assistant`, a branch `main` e o arquivo principal `web_app.py`.

Em **App settings → Secrets**, configure:

```toml
GROQ_API_KEY = "sua_chave_groq"
GROQ_MODEL = "llama-3.1-8b-instant"
```

Nunca publique chaves de API no repositório. O arquivo `.env` e os secrets locais estão incluídos no `.gitignore`.

## Limites e privacidade

- Até **4.000 caracteres** por solicitação.
- Intervalo mínimo de **15 segundos** entre solicitações.
- Até **15 solicitações por sessão**.
- Os controles por sessão não substituem um limite global contra abuso.
- Os textos são enviados ao provedor selecionado para processamento. Evite dados sensíveis.
- Não há armazenamento de histórico em banco de dados.

## Testes

```bash
python -m pytest -q
```

Os testes usam respostas simuladas e não consomem créditos de API.

## Desenvolvimento

O projeto reúne integração com APIs de modelos de linguagem, tratamento de erros, gerenciamento de credenciais, validação de entradas, testes e publicação de uma aplicação Python na web.

---

Desenvolvido por [Jonas Dzelme](https://github.com/Dzelmee).
