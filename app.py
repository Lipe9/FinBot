import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦", layout="centered")

# --- FUNÇÃO DE CONEXÃO ---
def get_model():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("❌ Erro: Chave de API não encontrada nos Secrets do Streamlit.")
        st.stop()

    modelos_para_tentar = [
        'gemini-2.0-flash',      
        'gemini-1.5-flash',   
        'gemini-1.5-pro'
    ]

    for nome_modelo in modelos_para_tentar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            return model, nome_modelo
        except Exception:
            continue
    
    st.error("⚠️ Não consegui conectar em nenhum modelo.")
    st.stop()

# --- INICIALIZAÇÃO DE DADOS ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar suas finanças?"}
    ]

model, nome_conectado = get_model()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.info(f"Conectado: {nome_conectado}")
    
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    st.subheader("Depositar")
    valor_dep = st.number_input("Valor:", min_value=0.0, step=10.0, key="dep")
    if st.button("Confirmar Depósito"):
        st.session_state.saldo_conta += valor_dep
        st.rerun()

    st.divider()

    st.subheader("Cofrinho")
    valor_cofre = st.number_input("Operação:", min_value=0.0, step=10.0, key="cof")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Guardar 📥"):
            if valor_cofre <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_cofre
                st.session_state.saldo_cofrinho += valor_cofre
                st.rerun()
    with c2:
        if st.button("Resgatar 📤"):
            if valor_cofre <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_cofre
                st.session_state.saldo_conta += valor_cofre
                st.rerun()

# --- CHAT PRINCIPAL ---
st.title("🤖 FinnBot: Assistente Financeiro")

# Container para as mensagens (para não sumirem)
chat_placeholder = st.container()

with chat_placeholder:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# Entrada de texto
if prompt := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_placeholder.chat_message("user"):
        st.write(prompt)

    with chat_placeholder.chat_message("assistant"):
        if "saldo" in prompt.lower():
            resposta = f"💰 Conta: R$ {st.session_state.saldo_conta:,.2f}\n🐷 Cofrinho: R$ {st.session_state.saldo_cofrinho:,.2f}"
        else:
            with st.spinner("Analisando..."):
                try:
                    instrucoes = f"Você é o FinnBot. Saldo conta: R$ {st.session_state.saldo_conta:.2f}. Saldo cofrinho: R$ {st.session_state.saldo_cofrinho:.2f}."
                    history = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]} for m in st.session_state.messages[-5:]]
                    chat = model.start_chat(history=history[:-1])
                    response = chat.send_message(f"{instrucoes}\n\nUsuário: {prompt}")
                    resposta = response.text
                except:
                    resposta = "Pode repetir? Tive um soluço técnico."

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# --- RODAPÉ ---
st.markdown("---")
st.caption("Developed by Felipe Silva.")
