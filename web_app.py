"""Interface web do assistente de texto."""
import os
import time

import streamlit as st
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from app import build_messages
from demo import EXAMPLES, demo_response
from provider import MAX_CHARS, generate_text

load_dotenv()
try:
    for name in ("GROQ_API_KEY", "GROQ_MODEL", "OPENAI_API_KEY", "OPENAI_MODEL"):
        if name in st.secrets and name not in os.environ:
            os.environ[name] = str(st.secrets[name])
except FileNotFoundError:
    pass
st.set_page_config(page_title="Texto — assistente de escrita", page_icon="✍️", layout="centered")

st.markdown(
    """
    <style>
    :root { color-scheme: dark; }
    .stApp { background: #10131a; color: #e8eaf0; }
    .block-container { max-width: 850px; padding-top: 3.4rem; padding-bottom: 3rem; }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    .eyebrow { color: #9da9bb; font-size: .76rem; letter-spacing: .19em; font-weight: 700; }
    .hero-title { font-size: clamp(2.4rem, 6vw, 4.1rem); line-height: 1.08;
                  font-weight: 750; letter-spacing: -.055em; margin: .9rem 0 .8rem; }
    .hero-title span { color: #a9c2f4; }
    .hero-copy { color: #aab4c4; font-size: 1.06rem; max-width: 580px;
                 line-height: 1.7; margin-bottom: 1.9rem; }
    .section-kicker { color: #c6d0df; font-size: .9rem; font-weight: 650;
                      margin: 1.3rem 0 .4rem; }
    .stTextArea textarea, [data-baseweb="select"] > div {
        background: #181e29 !important; border: 1px solid #30394a !important;
        border-radius: 12px !important; color: #f3f5f8 !important;
    }
    .stTextArea textarea:focus { border-color: #93b7ff !important; }
    .stForm { border: 1px solid #30394a; border-radius: 18px;
              background: #151a23; padding: 1.25rem; }
    .stButton button[kind="primary"], .stFormSubmitButton button {
        border-radius: 10px; font-weight: 650; min-height: 44px;
    }
    .stFormSubmitButton button { background: #b8d0ff; color: #101827; border: 0; }
    .stFormSubmitButton button:hover { background: #d4e2ff; color: #101827; }
    [data-testid="stExpander"] { background: #171d27; border: 1px solid #30394a;
                                  border-radius: 12px; }
    .footer-note { color: #8996a9; font-size: .83rem; line-height: 1.6;
                   margin-top: 2.5rem; border-top: 1px solid #30394a;
                   padding-top: 1.3rem; }
    @media (max-width: 640px) {
        .block-container { padding-top: 2rem; }
        .hero-copy { font-size: .98rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="eyebrow">TEXTO / FERRAMENTA DE ESCRITA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-title">Boas ideias merecem<br><span>palavras melhores.</span></div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-copy">Um espaço simples para organizar ideias, entender '
    'conteúdos e ajustar a escrita. Cole seu texto, escolha uma ação e pronto.</div>',
    unsafe_allow_html=True,
)

choices = {
    "Resumir": "1",
    "Explicar de forma simples": "2",
    "Revisar a escrita": "3",
}
mode_options = ["IA gratuita (Groq)", "Demonstração gratuita"]
if os.getenv("OPENAI_API_KEY", "").strip():
    mode_options.append("OpenAI API")
mode = st.radio(
    "Modo de uso",
    mode_options,
    horizontal=True,
    help="O modo demonstração usa respostas fixas e não faz chamadas à API.",
)
is_demo = mode == "Demonstração gratuita"

if is_demo:
    st.info(
        "Modo demonstração: os resultados são exemplos predefinidos, "
        "não respostas geradas por inteligência artificial. Nenhuma chamada à API é feita."
    )
elif mode == "IA gratuita (Groq)":
    st.caption("Use seus próprios textos com IA real. Serviço gratuito sujeito a limites de uso.")
    if not os.getenv("GROQ_API_KEY", "").strip():
        st.warning("A integração gratuita ainda não foi configurada pelo responsável pelo site.")
else:
    st.caption("Modo OpenAI: exige chave e créditos disponíveis na API.")

with st.form("assistant_form"):
    action = st.selectbox("O que você precisa?", list(choices))
    if is_demo:
        st.caption("Exemplo preenchido automaticamente. Para usar um texto próprio, selecione OpenAI API.")
        st.code(EXAMPLES[choices[action]]["input"], language=None, wrap_lines=True)
        user_text = EXAMPLES[choices[action]]["input"]
    else:
        user_text = st.text_area(
            "Texto",
            height=220,
            max_chars=MAX_CHARS,
            placeholder="Escreva ou cole seu texto aqui...",
            help=f"Até {MAX_CHARS} caracteres.",
        )
    submitted = st.form_submit_button(
        "Ver exemplo" if is_demo else "Processar texto",
        type="primary",
        use_container_width=True,
    )

if "history" not in st.session_state:
    st.session_state.history = []
if "last_request" not in st.session_state:
    st.session_state.last_request = 0.0
if "request_count" not in st.session_state:
    st.session_state.request_count = 0

if submitted:
    if is_demo:
        result = demo_response(choices[action], user_text)
        st.session_state.history.insert(0, (action, result, "Demonstração · resposta fixa"))
    elif not user_text.strip():
        st.warning("Adicione um texto para continuar.")
    elif time.monotonic() - st.session_state.last_request < 15:
        st.warning("Aguarde 15 segundos entre solicitações.")
    elif st.session_state.request_count >= 15:
        st.warning("Você atingiu o limite desta sessão.")
    elif mode == "IA gratuita (Groq)" and not os.getenv("GROQ_API_KEY", "").strip():
        st.error("A integração gratuita ainda não está configurada.")
    else:
        st.session_state.last_request = time.monotonic()
        st.session_state.request_count += 1
        try:
            provider = "groq" if mode == "IA gratuita (Groq)" else "openai"
            with st.spinner("Preparando resultado..."):
                result = generate_text(choices[action], user_text, provider)
            source = "Groq · IA real" if provider == "groq" else "OpenAI · IA real"
            st.session_state.history.insert(0, (action, result, source))
        except RateLimitError:
            st.error("O serviço atingiu seu limite gratuito. Tente novamente mais tarde.")
        except (APITimeoutError, APIConnectionError):
            st.error("Não foi possível conectar ao modelo. Tente novamente.")
        except APIStatusError:
            st.error("O serviço de IA está indisponível no momento.")
        except ValueError as exc:
            st.error(str(exc))

st.session_state.history = st.session_state.history[:10]

if st.session_state.history:
    st.markdown('<div class="section-kicker">Resultados recentes</div>', unsafe_allow_html=True)
    for index, (action, result, source) in enumerate(st.session_state.history):
        with st.expander(f"{action} · {source} · {index + 1}", expanded=index == 0):
            st.write(result)
            st.code(result, language=None)
    if st.button("Limpar resultados", type="secondary"):
        st.session_state.history = []
        st.rerun()

st.markdown(
    '<div class="footer-note">Projeto pessoal desenvolvido em Python + Streamlit. '
    'Os textos são enviados ao provedor selecionado. Evite dados sensíveis. O histórico fica nesta sessão. O plano gratuito tem limites.</div>',
    unsafe_allow_html=True,
)
