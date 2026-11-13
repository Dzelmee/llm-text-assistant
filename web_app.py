"""Interface web do assistente de texto."""
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

from app import build_messages
from demo import EXAMPLES, demo_response

load_dotenv()
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
mode = st.radio(
    "Modo de uso",
    ["Demonstração gratuita", "OpenAI API"],
    horizontal=True,
    help="O modo demonstração usa respostas fixas e não faz chamadas à API.",
)
is_demo = mode == "Demonstração gratuita"

if is_demo:
    st.info(
        "Modo demonstração: os resultados são exemplos predefinidos, "
        "não respostas geradas por inteligência artificial. Nenhuma chamada à API é feita."
    )
else:
    st.caption("Modo IA real: exige chave e créditos disponíveis na API da OpenAI.")

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
            max_chars=12000,
            placeholder="Escreva ou cole seu texto aqui...",
            help="Até 12.000 caracteres.",
        )
    submitted = st.form_submit_button(
        "Ver exemplo" if is_demo else "Processar texto",
        type="primary",
        use_container_width=True,
    )

if "history" not in st.session_state:
    st.session_state.history = []

if submitted:
    if is_demo:
        result = demo_response(choices[action], user_text)
        st.session_state.history.insert(0, (action, result, "Demonstração · resposta fixa"))
    elif not user_text.strip():
        st.warning("Adicione um texto para continuar.")
    elif not os.getenv("OPENAI_API_KEY"):
        st.error("Falta configurar OPENAI_API_KEY no arquivo .env.")
    else:
        try:
            messages = build_messages(choices[action], user_text)
            with st.spinner("Preparando resultado..."):
                response = OpenAI(
                    api_key=os.environ["OPENAI_API_KEY"], timeout=30.0
                ).chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=messages,
                    temperature=0.3,
                )
            result = response.choices[0].message.content or "Nenhum conteúdo retornado."
            st.session_state.history.insert(0, (action, result, "OpenAI API · resposta gerada"))
        except OpenAIError as exc:
            if getattr(exc, "status_code", None) == 429:
                st.error(
                    "A API retornou um limite de uso ou falta de créditos. "
                    "Você pode continuar usando o modo demonstração gratuitamente."
                )
            else:
                st.error("Não foi possível consultar a API. Confira sua configuração e tente novamente.")
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
    'O modo demonstração usa exemplos fixos. O histórico fica nesta sessão. O uso da API real pode gerar custos.</div>',
    unsafe_allow_html=True,
)
