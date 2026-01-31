import streamlit as st
import time
import google.generativeai as genai

# --- CONFIGURAÇÃO DA API (COLE SUA CHAVE AQUI) ---
GOOGLE_API_KEY = "AIzaSyA6_SDoYbPP9_54ncCGzjxKda-P1j16fMU"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="FinnBot AI", page_icon="🏦")

# --- INICIALIZAÇÃO DE DADOS ---
if 'saldo_conta' not in st.session_state:
    st.session_state.saldo_conta = 0.0
if 'saldo_cofrinho' not in st.session_state:
    st.session_state.saldo_cofrinho = 0.0
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu FinnBot, turbinado com IA. Como posso ajudar suas finanças hoje?"}]

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("🏦 Meu Painel")
    st.metric("Saldo em Conta", f"R$ {st.session_state.saldo_conta:,.2f}")
    st.metric("Guardado no Cofrinho 🐷", f"R$ {st.session_state.saldo_cofrinho:,.2f}")
    st.divider()
    
    st.subheader("Receber Saldo")
    valor_input_conta = st.number_input("Quanto deseja depositar?", min_value=0.0, step=100.0, key="add_conta")
    if st.button("Depositar na Conta"):
        st.session_state.saldo_conta += valor_input_conta
        st.success("Saldo atualizado!")
        time.sleep(1)
        st.rerun()

    st.divider()
    st.subheader("Gerenciar Cofrinho")
    valor_cofrinho = st.number_input("Valor da operação:", min_value=0.0, step=50.0, key="val_cofrinho")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Guardar 📥"):
            if valor_cofrinho <= st.session_state.saldo_conta:
                st.session_state.saldo_conta -= valor_cofrinho
                st.session_state.saldo_cofrinho += valor_cofrinho
                st.rerun()
    with c2:
        if st.button("Resgatar 📤"):
            if valor_cofrinho <= st.session_state.saldo_cofrinho:
                st.session_state.saldo_cofrinho -= valor_cofrinho
                st.session_state.saldo_conta += valor_cofrinho
                st.rerun()

# --- LÓGICA DE RENDIMENTO ---
def calcular_rendimento(valor, meses):
    taxa_mensal = 0.0085
    valor_final = valor * (1 + taxa_mensal) ** meses
    return valor_final, valor_final - valor

# --- INTERFACE DE CHAT ---
st.title("🤖 FinnBot: Assistente & Cofrinho")

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Pergunte sobre saldo, rendimento ou qualquer dúvida financeira!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        p_lower = prompt.lower()
        
        # 1. Tenta Lógica Local Primeiro (Ações Específicas)
        if "saldo" in p_lower:
            resposta = f"Seu saldo em conta é R$ {st.session_state.saldo_conta:,.2f} e no cofrinho R$ {st.session_state.saldo_cofrinho:,.2f}."
        
        elif "render" in p_lower or "rendimento" in p_lower:
            nums = [float(s) for s in p_lower.replace(",", ".").split() if s.replace(".", "").isdigit()]
            if len(nums) >= 2:
                v_final, v_lucro = calcular_rendimento(nums[0], nums[1])
                resposta = f"📈 Projeção: R$ {v_final:,.2f} (Lucro de R$ {v_lucro:,.2f})."
            else:
                resposta = "Para render, diga valor e meses. Ex: 'Quanto rende 1000 em 12 meses?'"
        
        # 2. Se não for comando específico, usa a Inteligência Artificial
        else:
            with st.spinner("Consultando inteligência financeira..."):
                try:
                    # System Prompt para guiar a personalidade da IA
                    contexto = (
                        f"Você é o FinnBot, um assistente financeiro. "
                        f"O saldo atual do usuário é R$ {st.session_state.saldo_conta:.2f}. "
                        "Responda de forma curta, útil e profissional."
                    )
                    full_prompt = f"{contexto}\nUsuário: {prompt}"
                    response = model.generate_content(full_prompt)
                    resposta = response.text
                except Exception as e:
                    resposta = "Ops, tive um problema ao conectar meu cérebro de IA. Tente novamente!"

        st.write(resposta)
        st.session_state.messages.append({"role": "assistant", "content": resposta})
