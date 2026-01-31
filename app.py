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
        st.error("❌ Erro: Chave de API não encontrada nos Secrets.")
        st.stop()
    
    # Modelos atualizados conforme sua lista
    modelos_para_tentar = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest']
    
    for nome_modelo in modelos_para_tentar:
        try:
            model = genai.GenerativeModel(nome_modelo)
            return model, nome_modelo
        except Exception:
            continue
    st.error("⚠️ Falha na conexão.")
    st.stop()

# --- INICIALIZAÇÃO DE ESTADO ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0

# Inicializa o chat atual
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar?"}]

# Inicializa a lista de conversas salvas (Histórico)
if 'historico_conversas' not in st.session_state:
    st.session_state.historico_conversas = []

model, nome_conectado = get_model()

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.success(f"⚡ {nome_conectado}")

    # BOTÃO: NOVO CHAT
    if st.button("➕ Abrir Novo Chat", use_container_width=True):
        # Salva a conversa atual no histórico antes de limpar (se houver mais que a mensagem inicial)
        if len(st.session_state.messages) > 1:
            timestamp = time.strftime("%H:%M:%S")
            resumo = st.session_state.messages[1]["content"][:30] + "..." # Pega o início da primeira pergunta
            st.session_state.historico_conversas.append({
                "label": f"Chat {timestamp}: {resumo}",
                "chats": list(st.session_state.messages)
            })
        
        # Reinicia as mensagens
        st.session_state.messages = [{"role": "assistant", "content": "Novo chat iniciado! Como posso ajudar?"}]
        st.rerun()

    st.divider()
    
    # MENU: HISTÓRICO DE RESPOSTAS
    st.subheader("📜 Histórico")
    if not st.session_state.historico_conversas:
        st.info("Nenhuma conversa salva.")
    else:
        for i, conversa in enumerate(reversed(st.session_state.historico_conversas)):
            if st.button(conversa["label"], key=f"hist_{i}", use_container_width=True):
                st.session_state.messages = list(conversa["chats"])
                st.rerun()

    st.divider()
    
    # FINANCEIRO
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    # (Omiti botões de depósito/guardar para encurtar, mas você deve mantê-los aqui)

# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Assistente")

# Renderiza as mensagens
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Pergunte algo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            try:
                instrucoes = f"Você é o FinnBot. Saldo: R$ {st.session_state.saldo_conta:.2f}."
                
                # Prepara histórico para o Gemini
                history_gemini = []
                for m in st.session_state.messages[-6:]:
                    role = "model" if m["role"] == "assistant" else "user"
                    history_gemini.append({"role": role, "parts": [m["content"]]})

                chat = model.start_chat(history=history_gemini[:-1])
                response = chat.send_message(f"{instrucoes}\n\nPergunta: {prompt}")
                resposta = response.text
            except Exception:
                resposta = "Tive um problema técnico. Tente novamente."

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
