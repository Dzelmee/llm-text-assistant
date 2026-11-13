# Texto.

Criei o **Texto.** para reunir três tarefas de escrita em um só lugar: resumir, explicar e revisar textos. Queria uma ferramenta que fosse simples de abrir e usar, sem exigir instalação nem cadastro.

**[Testar o Texto.](https://llm-text-assistant-dzelmee.streamlit.app/)**

## O que dá para fazer

- **Resumir:** escolher entre um resumo curto, médio ou detalhado.
- **Explicar:** reescrever um conteúdo em linguagem mais simples.
- **Revisar:** melhorar a escrita sem perder a ideia original.
- **Consultar resultados:** ver as últimas respostas da sessão e copiar o texto.
- **Experimentar sem API:** usar o modo demonstração com exemplos prontos.

Também trabalhei na identidade visual: cores suaves, layout responsivo e um pequeno mascote que acompanha as letras do título. Para essa animação, usei JavaScript dentro de um componente HTML incorporado ao Streamlit.

## Tecnologias

- **Python e Streamlit:** interface, fluxo das ações e estado da sessão.
- **Groq API:** geração de respostas com o modelo `openai/gpt-oss-20b`; há uma tentativa alternativa com `openai/gpt-oss-120b` se o modelo configurado não for encontrado.
- **HTML, CSS e JavaScript:** estilo, responsividade e animação do mascote.
- **OpenAI API:** opção adicional, configurada separadamente.
- **pytest e GitHub Actions:** testes automatizados e verificações do repositório.

## Como o projeto funciona

Depois de escolher uma ação e enviar o texto, a aplicação valida a entrada, monta a instrução e chama a API selecionada. A resposta aparece formatada na página e fica disponível no histórico da sessão.

Uma parte importante do desenvolvimento foi lidar com os erros da integração. Precisei atualizar modelos que deixaram de funcionar, distinguir falhas da API e ajustar o processamento de respostas vazias. Também acrescentei os três tamanhos de resumo e simplifiquei a forma de copiar os resultados.

## Rodar no computador

É necessário ter **Python 3.10 ou superior**.

```bash
git clone https://github.com/Dzelmee/llm-text-assistant.git
cd llm-text-assistant
python -m venv .venv
```

Ative o ambiente virtual no Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Ou no Linux/macOS:

```bash
source .venv/bin/activate
```

Instale as dependências e execute:

```bash
pip install -r requirements.txt
streamlit run web_app.py
```

Para usar a IA, copie `.env.example` para `.env` e configure `GROQ_API_KEY`. Sem chave, ainda é possível abrir o modo demonstração.

## Publicar no Streamlit Community Cloud

Configure o repositório `Dzelmee/llm-text-assistant`, a branch `main` e o arquivo principal `web_app.py`.

Nas configurações de **Secrets**, use:

```toml
GROQ_API_KEY = "sua_chave_groq"
GROQ_MODEL = "openai/gpt-oss-20b"
```

Nunca coloque chaves reais no GitHub. O `.env` está ignorado pelo Git.

## Limites e privacidade

- Máximo de **4.000 caracteres** por texto.
- Intervalo de **15 segundos** entre solicitações.
- Limite de **15 solicitações por sessão**.
- O histórico fica na sessão do Streamlit; não há banco de dados para armazená-lo.
- Os textos são enviados ao provedor de IA escolhido. Evite inserir informações sensíveis.

Esses limites são por sessão e não substituem uma proteção global contra uso abusivo. A API gratuita da Groq também está sujeita aos limites do próprio serviço.

## Testes

```bash
python -m pytest -q
```

Os testes utilizam respostas simuladas, sem fazer chamadas reais às APIs.

---

Desenvolvido por [Jonas Dzelme](https://github.com/Dzelmee).
