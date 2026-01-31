import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA API ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Erro na configuração da IA: {e}")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦")

# --- INICIALIZAÇÃO DE DADOS (Persistência) ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou seu FinnBot. Como posso ajudar suas finanças hoje?"}
    ]

# --- BARRA LATERAL (Painel Financeiro) ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("No Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    
    st.divider()
    
    st.subheader("Depositar")
    valor_dep = st.number_input("Valor:", min_value=0.0, step=100.0, key="dep")
    if st.button("Confirmar Depósito"):
        st.session_state.saldo_conta += valor_dep
        st.success("Saldo atualizado!")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    st.subheader("Cofrinho")
    valor_cofre = st.number_input("Operação cofrinho:", min_value=0.0, step=50.0, key="cof")
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

# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Seu Assistente")

# Exibe o histórico de mensagens
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Entrada de novas mensagens
if prompt := st.chat_input("Pergunte qualquer coisa!"):
    # Adiciona pergunta do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()
        
        # 1. Comandos Locais (Saldo)
        if "saldo" in p_lower:
            resposta = f"Seu saldo é R$ {st.session_state.saldo_conta:,.2f} e no cofrinho há R$ {st.session_state.saldo_cofrinho:,.2f}."
        
        # 2. Inteligência Artificial com Memória
        else:
            with st.spinner("Processando..."):
                try:
                    # Contexto do Sistema (Diz à IA quem ela é e quanto dinheiro o usuário tem)
                    instrucoes = (
                        f"Você é o FinnBot, um assistente financeiro. "
                        f"O usuário tem R$ {st.session_state.saldo_conta:.2f} na conta. "
                        "Dê respostas curtas, amigáveis e em português."
                    )
                    
                    # Formata o histórico para o padrão que o Gemini aceita (user/model)
                    historico_gemini = []
                    for m in st.session_state.messages[-6:]: # Últimas 6 mensagens
                        role = "user" if m["role"] == "user" else "model"
                        historico_gemini.append({"role": role, "parts": [m["content"]]})
                    
                    # Inicia a sessão de chat
                    chat = model.start_chat(history=historico_gemini[:-1])
                    response = chat.send_message(f"{instrucoes}\n\nPergunta: {prompt}")
                    resposta = response.text
                    
                except Exception as e:
                    # Caso a memória falhe (Erro 404), tenta uma resposta direta sem histórico
                    try:
                        res = model.generate_content(f"{instrucoes}\n\n{prompt}")
                        resposta = res.text
                    except Exception as e2:
                        st.error(f"Erro na API: {e2}")
                        resposta = "Infelizmente não consegui me conectar agora. Tente de novo em um minuto."

        # Exibe a resposta e salva na memória
        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
