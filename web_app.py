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
    .stApp {
        background: radial-gradient(ellipse at 75% 0%, #28342b 0%, transparent 45%),
                    #151a17;
        color: #f1eee6;
    }
    /* Luz ambiente fixa atrás do conteúdo. */
    .stApp { isolation: isolate; }
    .stApp::before, .stApp::after {
        content: ""; position: fixed; pointer-events: none;
        z-index: -1; border-radius: 50%;
        filter: blur(65px); opacity: .35;
        animation: ambient-drift 22s ease-in-out infinite alternate;
    }
    .stApp::before {
        width: min(52vw, 650px); height: min(52vw, 650px);
        left: -17vw; top: 13vh;
        background: radial-gradient(circle, #526b48 0%, transparent 70%);
    }
    .stApp::after {
        width: min(58vw, 720px); height: min(58vw, 720px);
        right: -19vw; top: -12vh;
        background: radial-gradient(circle, #526d57 0%, transparent 70%);
        animation-delay: -9s; animation-duration: 29s;
    }
    .block-container { max-width: 850px; padding-top: 3rem; padding-bottom: 3rem;
                       position: relative; }
    .block-container::before {
        content: ""; position: fixed; pointer-events: none; z-index: -1;
        width: min(40vw, 470px); height: min(40vw, 470px);
        right: 4vw; bottom: -22vh; border-radius: 50%;
        background: radial-gradient(circle, #877f51 0%, transparent 70%);
        filter: blur(65px); opacity: .18;
        animation: ambient-drift 31s ease-in-out infinite alternate-reverse;
    }
    .block-container::after {
        content: ""; position: fixed; pointer-events: none; z-index: -1; inset: 0;
        background-image: radial-gradient(#b9c9a5 0.65px, transparent 0.65px);
        background-size: 26px 26px; opacity: .055;
        mask-image: linear-gradient(90deg, black, transparent 45%, transparent 60%, black);
    }
    @keyframes ambient-drift {
        from { transform: translate3d(-15px, 10px, 0) scale(1); }
        to { transform: translate3d(55px, -35px, 0) scale(1.15); }
    }
    header[data-testid="stHeader"] { background: transparent; }
    #MainMenu, footer { visibility: hidden; }
    .eyebrow { color: #b4c8ac; font-size: .74rem; letter-spacing: .19em; font-weight: 750; }
    .hero-title { font-size: clamp(1.4rem, 5.8vw, 4.1rem); line-height: 1.08;
                  font-weight: 750; letter-spacing: -.055em; margin: .75rem 0 .8rem; }
    .hero-title span { color: #c2d6ad; }
    .hero-first-line { display: block; position: relative; width: fit-content;
                       max-width: 100%; white-space: nowrap; margin-top: 4.4rem; }
    .hero-first-line .headline-text { color: #f1eee6; }
    .walking-mascot { position: absolute; width: 38px; height: 54px;
                      bottom: calc(100% - .12em); left: 0; pointer-events: none;
                      z-index: 3; transform-origin: center bottom;
                      animation: mascot-route 16s linear infinite; }
    .walking-mascot .wm-head { position: absolute; top: 3px; left: 3px;
                               width: 32px; height: 32px; border-radius: 13px;
                               background: #bdd5a9; z-index: 4; }
    .walking-mascot .wm-leaf { position: absolute; top: -4px; left: 19px;
                               width: 9px; height: 14px; background: #8faa80;
                               border-radius: 100% 0 100% 0; transform: rotate(-25deg);
                               z-index: 5; }
    .walking-mascot .wm-eye { position: absolute; top: 13px; width: 4px;
                              height: 5px; border-radius: 50%; background: #263729;
                              animation: mascot-blink 5s infinite; }
    .walking-mascot .wm-eye:first-child { left: 9px; }
    .walking-mascot .wm-eye:nth-child(2) { right: 9px; }
    .walking-mascot .wm-smile { position: absolute; top: 21px; left: 12px;
                                width: 9px; height: 5px; border-bottom: 2px solid #263729;
                                border-radius: 50%; }
    .walking-mascot .wm-body { position: absolute; top: 33px; left: 12px;
                               width: 15px; height: 11px; border-radius: 7px;
                               background: #91ac86; z-index: 2; }
    .walking-mascot .wm-arm, .walking-mascot .wm-leg {
        position: absolute; width: 5px; background: #bdd5a9;
        border-radius: 4px; transform-origin: top center;
        animation: mascot-step .55s ease-in-out infinite alternate;
    }
    .walking-mascot .wm-arm { top: 35px; height: 10px; }
    .walking-mascot .wm-leg { top: 43px; height: 11px; background: #91ac86; }
    .walking-mascot .wm-left.wm-arm { left: 9px; }
    .walking-mascot .wm-right.wm-arm { right: 9px; animation-delay: -.55s; }
    .walking-mascot .wm-left.wm-leg { left: 13px; }
    .walking-mascot .wm-right.wm-leg { right: 13px; animation-delay: -.55s; }
    @keyframes mascot-step {
        from { transform: rotate(-24deg); } to { transform: rotate(24deg); }
    }
    /* Saltos arredondados nos dois espaços; a posição horizontal nunca
       ultrapassa a largura da frase. */
    @keyframes mascot-route {
        0%, 3% { left: 0; transform: translateY(0) scaleX(1); }
        17% { left: 17%; transform: translateY(0) scaleX(1); }
        21% { left: 22%; transform: translateY(-10px) scaleX(1); }
        25% { left: 27%; transform: translateY(0) scaleX(1); }
        33% { left: 43%; transform: translateY(0) scaleX(1); }
        37% { left: 48%; transform: translateY(-10px) scaleX(1); }
        41% { left: 53%; transform: translateY(0) scaleX(1); }
        47% { left: calc(100% - 38px); transform: translateY(0) scaleX(1); }
        50% { left: calc(100% - 38px); transform: translateY(0) scaleX(-1); }
        53% { left: calc(100% - 38px); transform: translateY(0) scaleX(-1); }
        59% { left: 53%; transform: translateY(0) scaleX(-1); }
        63% { left: 48%; transform: translateY(-10px) scaleX(-1); }
        67% { left: 43%; transform: translateY(0) scaleX(-1); }
        75% { left: 27%; transform: translateY(0) scaleX(-1); }
        79% { left: 22%; transform: translateY(-10px) scaleX(-1); }
        83% { left: 17%; transform: translateY(0) scaleX(-1); }
        97% { left: 0; transform: translateY(0) scaleX(-1); }
        100% { left: 0; transform: translateY(0) scaleX(1); }
    }

    .hero-copy { color: #c0c8bc; font-size: 1.06rem; max-width: 580px;
                 line-height: 1.7; margin-bottom: 1.7rem; }
    .section-kicker { color: #d9e2d2; font-size: .95rem; font-weight: 650;
                      margin: 1.3rem 0 .4rem; }
    .stTextArea textarea {
        background: #202922 !important; border: 1px solid #445447 !important;
        border-radius: 14px !important; color: #f4f1e9 !important;
    }
    .stTextArea textarea:focus { border-color: #a8c49a !important;
                                box-shadow: 0 0 0 1px #a8c49a !important; }
    .stForm { border: 1px solid #3b4c3d; border-radius: 20px;
              background: #1c251f; padding: 1.35rem; }
    div[data-testid="stRadio"] [role="radiogroup"] { gap: .65rem; }
    div[data-testid="stRadio"] label {
        border: 1px solid #4a5b4c; background: #202b23; border-radius: 12px;
        padding: .65rem .95rem; transition: background .2s, border-color .2s, transform .2s;
    }
    div[data-testid="stRadio"] label:hover {
        background: #2c3a30; border-color: #a8c49a; transform: translateY(-2px);
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        background: #304132; border-color: #b6d1a6;
    }
    .stButton button[kind="primary"], .stFormSubmitButton button {
        border-radius: 12px; font-weight: 700; min-height: 48px;
    }
    .stFormSubmitButton button { background: #bdd5a9; color: #192219; border: 0; }
    .stFormSubmitButton button:hover { background: #d3e5c1; color: #192219; }
    [data-testid="stExpander"] { background: #202a23; border: 1px solid #445447;
                                  border-radius: 14px; }
    .footer-note { color: #a1afa0; font-size: .83rem; line-height: 1.6;
                   margin-top: 2.5rem; border-top: 1px solid #3b4c3d;
                   padding-top: 1.3rem; }
    .brand-row { display: flex; align-items: center; gap: 1.1rem; margin-bottom: 1.2rem; }
    .mascot { position: relative; flex: 0 0 76px; height: 76px;
              background: #bdd5a9; border-radius: 28px 28px 24px 24px;
              transform: rotate(-6deg); box-shadow: 0 10px 30px #0003;
              animation: mascot-float 3.5s ease-in-out infinite; }
    .mascot:before, .mascot:after { content: ""; position: absolute; top: 31px;
                                    width: 8px; height: 10px; background: #263729;
                                    border-radius: 50%; animation: mascot-blink 5s infinite; }
    .mascot:before { left: 23px; } .mascot:after { right: 23px; }
    .mascot-smile { position: absolute; left: 31px; top: 43px; width: 16px; height: 9px;
                    border-bottom: 3px solid #263729; border-radius: 0 0 50% 50%; }
    .mascot-leaf { position: absolute; top: -13px; left: 35px; width: 20px; height: 24px;
                   background: #8faa80; border-radius: 100% 0 100% 0;
                   transform: rotate(-25deg); }
    .mascot-name { font-weight: 800; font-size: 1.3rem; letter-spacing: -.04em; }
    .mascot-caption { font-size: .82rem; color: #aebda8; }
    @keyframes mascot-float { 0%,100% { transform: translateY(0) rotate(-6deg); }
                              50% { transform: translateY(-7px) rotate(-2deg); } }
    @keyframes mascot-blink { 0%,44%,48%,100% { transform: scaleY(1); }
                              46% { transform: scaleY(.12); } }
    @media (prefers-reduced-motion: reduce) {
        .stApp::before, .stApp::after, .block-container::before { animation: none; }
        .mascot, .mascot:before, .mascot:after { animation: none; }
        .walking-mascot, .walking-mascot .wm-arm, .walking-mascot .wm-leg { animation: none; }
        div[data-testid="stRadio"] label { transition: none; }
    }
    @media (max-width: 640px) {
        .block-container { padding-top: 1.8rem; }
        .hero-copy { font-size: .98rem; }
        .mascot { flex-basis: 62px; height: 62px; }
        .mascot:before, .mascot:after { top: 24px; }
        .mascot:before { left: 18px; } .mascot:after { right: 18px; }
        .mascot-smile { left: 24px; top: 36px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand-row"><div class="mascot" aria-hidden="true">'
    '<div class="mascot-leaf"></div><div class="mascot-smile"></div></div>'
    '<div><div class="mascot-name">texto<span style="color:#bdd5a9">.</span></div>'
    '<div class="mascot-caption">Seu companheiro de escrita</div></div></div>',
    unsafe_allow_html=True,
)
st.markdown('<div class="eyebrow">TEXTO / FERRAMENTA DE ESCRITA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-title"><span class="hero-first-line">'
    '<span class="headline-text">Boas ideias merecem</span>'
    '<span class="walking-mascot" aria-hidden="true">'
    '<span class="wm-leaf"></span><span class="wm-head">'
    '<i class="wm-eye"></i><i class="wm-eye"></i><i class="wm-smile"></i></span>'
    '<span class="wm-arm wm-left"></span><span class="wm-arm wm-right"></span>'
    '<span class="wm-body"></span>'
    '<span class="wm-leg wm-left"></span><span class="wm-leg wm-right"></span>'
    '</span></span><span>palavras melhores.</span></div>',
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
    help="A IA gratuita usa uma API com cotas; a demonstração mostra respostas fixas.",
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
    action = st.radio(
        "O que você precisa?",
        list(choices),
        horizontal=True,
        help="Escolha uma das três ações. Não é necessário digitar nesta seleção.",
    )
    if is_demo:
        st.caption("Exemplo preenchido automaticamente. Para usar um texto próprio, selecione IA gratuita (Groq).")
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
