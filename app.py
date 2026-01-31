import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦")

# --- FUNÇÃO DE CONEXÃO ---
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada.")
        st.stop()
    
    modelos = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    for nome in modelos:
        try:
            return genai.GenerativeModel(nome), nome
        except: continue
    st.stop()

# --- INICIALIZAÇÃO DE ESTADO ---
if 'saldo_conta' not in st.session_state: st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state: st.session_state.saldo_cofrinho = 0.0
# Estados para Metas
if 'nome_meta' not in st.session_state: st.session_state.nome_meta = ""
if 'valor_meta' not in st.session_state: st.session_state.valor_meta = 0.0

if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar?"}]
if 'historico_conversas' not in st.session_state:
    st.session_state.historico_conversas = []

model, nome_conectado = get_model()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.caption(f"Conectado: {nome_conectado}")

    # --- SEÇÃO DE CHAT ---
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        if st.button("➕ Novo Chat", use_container_width=True):
            if len(st.session_state.messages) > 1:
                resumo = st.session_state.messages[1]["content"][:20]
                st.session_state.historico_conversas.append({
                    "label": f"🕒 {time.strftime('%H:%M')} - {resumo}...",
                    "chats": list(st.session_state.messages)
                })
            st.session_state.messages = [{"role": "assistant", "content": "Novo chat! Como posso ajudar?"}]
            st.rerun()
    
    with col_n2:
        if st.button("🗑️ Limpar", use_container_width=True):
            st.session_state.historico_conversas = []
            st.session_state.messages = [{"role": "assistant", "content": "Histórico apagado. Vamos recomeçar?"}]
            st.rerun()

    with st.expander("📜 Conversas Anteriores"):
        for i, conversa in enumerate(reversed(st.session_state.historico_conversas)):
            if st.button(conversa["label"], key=f"h_{i}", use_container_width=True):
                st.session_state.messages = list(conversa["chats"])
                st.rerun()

    st.divider()

    # --- SEÇÃO DE METAS ---
    st.subheader("🎯 Minha Meta")
    with st.expander("Configurar Meta"):
        nome_m = st.text_input("Objetivo:", value=st.session_state.nome_meta, placeholder="Ex: Viagem, PS5...")
        valor_m = st.number_input("Valor Alvo (R$):", min_value=0.0, value=st.session_state.valor_meta, step=100.0)
        if st.button("Salvar Meta", use_container_width=True):
            st.session_state.nome_meta = nome_m
            st.session_state.valor_meta = valor_m
            st.success("Meta salva!")
            st.rerun()

    if st.session_state.valor_meta > 0:
        progresso = min(st.session_state.saldo_cofrinho / st.session_state.valor_meta, 1.0)
        st.write(f"**{st.session_state.nome_meta}**")
        st.progress(progresso)
        st.caption(f"R$ {st.session_state.saldo_cofrinho:,.2f} de R$ {st.session_state.valor_meta:,.2f} ({progresso*100:.1f}%)")
    else:
        st.info("Crie uma meta acima!")

    st.divider()

    # --- SEÇÃO FINANCEIRA ---
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")

    st.subheader("💳 Transações")
    valor = st.number_input("Valor da operação:", min_value=0.0, step=50.0)
    
    if st.button("💰 Depositar na Conta", use_container_width=True):
        st.session_state.saldo_conta += valor
        st.success("Valor depositado!")
        time.sleep(0.5); st.rerun()

    st.write("---")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        if st.button("📥 Guardar", use_container_width=True):
            if valor <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor
                st.session_state.saldo_cofrinho += valor
                st.rerun()
            else: st.error("Saldo insuficiente")
    with col_c2:
        if st.button("📤 Resgatar", use_container_width=True):
            if valor <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor
                st.session_state.saldo_conta += valor
                st.rerun()
            else: st.error("Cofrinho vazio")

# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Assistente Financeiro")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Diga algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            try:
                # O FinnBot agora também sabe sobre a meta do usuário
                ctx = (f"Você é o FinnBot. Saldo: R$ {st.session_state.saldo_conta:.2f}. "
                       f"Meta atual: {st.session_state.nome_meta} de R$ {st.session_state.valor_meta:.2f}. "
                       f"Já guardou R$ {st.session_state.saldo_cofrinho:.2f}.")
                
                hist = []
                for m in st.session_state.messages[-6:]:
                    r = "model" if m["role"] == "assistant" else "user"
                    hist.append({"role": r, "parts": [m["content"]]})
                
                chat = model.start_chat(history=hist[:-1])
                response = chat.send_message(f"{ctx}\n\nPergunta: {prompt}")
                resposta = response.text
            except:
                resposta = "Estou com instabilidade. Tente novamente."

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
