"""Interface web do assistente de texto."""
import os
import time
import logging

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, APITimeoutError, RateLimitError

from app import build_messages
from demo import EXAMPLES, demo_response
from provider import MAX_CHARS, generate_text

load_dotenv()
logger = logging.getLogger(__name__)
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
    .hero-title .walking-mascot { color: initial; }
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
components.html(
    """
    <!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
    <style>
      *{box-sizing:border-box}html,body{margin:0;padding:0;background:transparent;overflow:hidden}
      body{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#f1eee6}
      .stage{position:relative;margin-top:63px;width:max-content;max-width:100%}
      .phrase,.second{font-size:clamp(22px,5.8vw,65px);font-weight:750;letter-spacing:-.055em;line-height:1.12;white-space:nowrap}
      .second{color:#c2d6ad}
      .walker{position:absolute;left:0;top:0;width:38px;height:54px;pointer-events:none;will-change:transform;transform-origin:center bottom}
      .head{position:absolute;top:3px;left:3px;width:32px;height:32px;background:#bdd5a9;border-radius:13px;z-index:4}
      .leaf{position:absolute;top:-4px;left:19px;width:9px;height:14px;background:#8faa80;border-radius:100% 0 100% 0;transform:rotate(-25deg);z-index:5}
      .eye{position:absolute;top:13px;width:4px;height:5px;background:#263729;border-radius:50%;animation:blink 5s infinite}
      .e1{left:9px}.e2{right:9px}
      .smile{position:absolute;top:21px;left:12px;width:9px;height:5px;border-bottom:2px solid #263729;border-radius:50%}
      .body{position:absolute;top:33px;left:12px;width:15px;height:11px;background:#91ac86;border-radius:7px;z-index:2}
      .arm,.leg{position:absolute;width:5px;border-radius:4px;transform-origin:top;animation:swing .55s ease-in-out infinite alternate}
      .arm{top:35px;height:10px;background:#bdd5a9}.leg{top:43px;height:11px;background:#91ac86}
      .a1{left:9px}.a2{right:9px;animation-delay:-.55s}.l1{left:13px}.l2{right:13px;animation-delay:-.55s}
      @keyframes swing{from{transform:rotate(-24deg)}to{transform:rotate(24deg)}}
      @keyframes blink{0%,44%,48%,100%{transform:scaleY(1)}46%{transform:scaleY(.12)}}
      @media(max-width:500px){.stage{margin-top:62px}.phrase,.second{font-size:clamp(18px,5.5vw,30px)}}
    </style></head><body>
      <div class="stage"><div class="phrase">Boas ideias merecem</div>
        <div class="walker" aria-hidden="true"><div class="leaf"></div><div class="head">
          <i class="eye e1"></i><i class="eye e2"></i><i class="smile"></i></div>
          <div class="arm a1"></div><div class="arm a2"></div><div class="body"></div>
          <div class="leg l1"></div><div class="leg l2"></div></div>
      </div><div class="second">palavras melhores.</div>
      <script>
        const phrase=document.querySelector('.phrase'),walker=document.querySelector('.walker');
        const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d',{willReadFrequently:true});
        let surface=[],spaces=[],start=0,last=0,currentY=null;
        const smooth=u=>{u=Math.max(0,Math.min(1,u));return u*u*(3-2*u)};
        function measure(){
          const cs=getComputedStyle(phrase),r=phrase.getBoundingClientRect(),dpr=2;
          canvas.width=Math.ceil(r.width*dpr);canvas.height=Math.ceil(r.height*dpr);
          ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,r.width,r.height);
          ctx.fillStyle='white';ctx.font=cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;
          ctx.textBaseline='alphabetic';
          const spacing=parseFloat(cs.letterSpacing)||0,baseline=parseFloat(cs.fontSize)*.86;
          let x=0;spaces=[];
          for(const ch of phrase.textContent){
            const width=ctx.measureText(ch).width+spacing;
            if(ch===' ')spaces.push({start:x,end:x+width});
            else ctx.fillText(ch,x,baseline);
            x+=width;
          }
          const pixels=ctx.getImageData(0,0,canvas.width,canvas.height).data;
          surface=[];
          for(let ix=0;ix<canvas.width;ix++){
            let top=null;
            for(let iy=0;iy<canvas.height;iy++){
              if(pixels[(iy*canvas.width+ix)*4+3]>90){top=iy/dpr;break}
            }
            surface.push(top);
          }
        }
        function ground(x){
          const scale=canvas.width/Math.max(1,phrase.getBoundingClientRect().width);
          const center=Math.round(x*scale),radius=Math.round(5*scale);
          let sum=0,weights=0;
          for(let i=Math.max(0,center-radius);i<=Math.min(surface.length-1,center+radius);i++){
            if(surface[i]===null)continue;
            const weight=1-Math.abs(i-center)/(radius+1);
            sum+=surface[i]*weight;weights+=weight;
          }
          return weights?sum/weights:null;
        }
        function animate(now){
          if(!start)start=now;
          const dt=last?Math.min((now-last)/1000,.05):.016;last=now;
          const t=((now-start)/16000)%1;
          const width=phrase.getBoundingClientRect().width;
          const range=Math.max(0,width-38);
          let progress,dir,moving;
          if(t<.44){progress=smooth(t/.44);dir=1;moving=true}
          else if(t<.5){progress=1;dir=1;moving=false}
          else if(t<.94){progress=1-smooth((t-.5)/.44);dir=-1;moving=true}
          else{progress=0;dir=-1;moving=false}
          const x=range*progress,foot=x+19;
          const fs=parseFloat(getComputedStyle(phrase).fontSize);
          let y=ground(foot);if(y===null)y=fs*.20;
          let jump=0;
          for(const gap of spaces){
            const margin=Math.max(10,fs*.22),left=gap.start-margin,right=gap.end+margin;
            if(foot>=left&&foot<=right){
              const u=(foot-left)/(right-left);
              jump=Math.max(jump,Math.sin(Math.PI*smooth(u))*Math.min(13,fs*.3));
            }
          }
          const step=moving?Math.abs(Math.sin(now*.008))*.8:0;
          const target=y-54-jump-step;
          if(currentY===null)currentY=target;
          currentY+=(target-currentY)*(1-Math.exp(-dt*10));
          walker.style.transform='translate3d('+x+'px,'+currentY+'px,0) scaleX('+dir+')';
          requestAnimationFrame(animate);
        }
        measure();
        new ResizeObserver(measure).observe(phrase);
        document.fonts.ready.then(measure);
        requestAnimationFrame(animate);
      </script>
    </body></html>
    """,
    height=202,
    scrolling=False,
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

action = st.radio(
    "O que você precisa?",
    list(choices),
    horizontal=True,
    help="Escolha uma das três ações.",
)
with st.form("assistant_form"):
    summary_length = "Médio"
    if action == "Resumir":
        summary_length = st.radio(
            "Tamanho do resumo",
            ["Curto", "Médio", "Detalhado"],
            horizontal=True,
            help="Curto: até 70 palavras. Médio: 100 a 150. Detalhado: 200 a 300.",
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
                result = generate_text(choices[action], user_text, provider, summary_length=summary_length)
            source = "Groq · IA real" if provider == "groq" else "OpenAI · IA real"
            st.session_state.history.insert(0, (action, result, source))
        except RateLimitError as exc:
            logger.warning("Limite da API atingido: HTTP %s", exc.status_code)
            st.error("O limite de uso da IA foi atingido. Aguarde alguns minutos e tente novamente.")
        except (APITimeoutError, APIConnectionError) as exc:
            logger.warning("Falha de conexão com a IA: %s", type(exc).__name__)
            st.error("Não foi possível conectar à IA. Verifique sua conexão e tente novamente.")
        except APIStatusError as exc:
            error_body = exc.body if isinstance(exc.body, dict) else {}
            error_details = error_body.get("error", {})
            if not isinstance(error_details, dict):
                error_details = {}
            api_error_code = error_details.get("code")
            safe_code = str(api_error_code)[:80] if isinstance(api_error_code, (str, int)) else "não informado"
            configured_model = (os.getenv("GROQ_MODEL", "").strip() or "openai/gpt-oss-20b") if provider == "groq" else (os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini")
            logger.warning("Falha da API %s: HTTP %s, modelo %s, código %s",
                           provider, exc.status_code, configured_model, safe_code)
            if exc.status_code == 400:
                st.error("A solicitação foi recusada pelo modelo de IA. O responsável pelo site precisa verificar a configuração do modelo.")
            elif exc.status_code in (401, 403):
                st.error("A autenticação do serviço de IA falhou. O responsável pelo site precisa verificar a chave de acesso.")
            elif exc.status_code == 404:
                st.error("A Groq retornou HTTP 404 mesmo após a tentativa com o modelo alternativo. Confira a configuração do serviço.")
                with st.expander("Detalhes para diagnóstico"):
                    st.code(f"HTTP: {exc.status_code}\\nModelo configurado: {configured_model}\\nModelo alternativo: openai/gpt-oss-120b\\nCódigo da API: {safe_code}", language=None)
                    st.caption("Esses dados não incluem sua chave de API nem o texto enviado.")
            elif exc.status_code == 422:
                st.error("A IA não conseguiu processar esta solicitação. Tente um texto mais curto.")
            elif exc.status_code >= 500:
                st.error("O provedor de IA está com instabilidade. Tente novamente em alguns minutos.")
            else:
                st.error(f"O serviço de IA recusou a solicitação (código {exc.status_code}). Tente novamente mais tarde.")
        except ValueError as exc:
            st.error(str(exc))

st.session_state.history = st.session_state.history[:10]

if st.session_state.history:
    st.markdown('<div class="section-kicker">Resultados recentes</div>', unsafe_allow_html=True)
    for index, (action, result, source) in enumerate(st.session_state.history):
        with st.expander(f"{action} · {source} · {index + 1}", expanded=index == 0):
            st.markdown(result)
            with st.popover("Copiar resultado"):
                st.caption("Use o ícone de copiar no canto do bloco abaixo.")
                st.code(result, language=None, wrap_lines=True)
    if st.button("Limpar resultados", type="secondary"):
        st.session_state.history = []
        st.rerun()

st.markdown(
    '<div class="footer-note">Projeto pessoal desenvolvido em Python + Streamlit. '
    'Os textos são enviados ao provedor selecionado. Evite dados sensíveis. O histórico fica nesta sessão. O plano gratuito tem limites.</div>',
    unsafe_allow_html=True,
)
