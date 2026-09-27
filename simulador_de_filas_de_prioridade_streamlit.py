import random
from collections import deque
import pandas as pd
import streamlit as st

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Simulador de Filas de Prioridade",
    page_icon="🚦",
    layout="wide"
)

# Estilização CSS para badges e cartões de itens
st.markdown("""
<style>
    .item-card {
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 500;
        font-family: monospace;
    }
    .prio-3 {
        background-color: rgba(239, 68, 68, 0.15);
        border-left: 5px solid #ef4444;
        color: #b91c1c;
    }
    .prio-2 {
        background-color: rgba(245, 158, 11, 0.15);
        border-left: 5px solid #f59e0b;
        color: #b45309;
    }
    .prio-1 {
        background-color: rgba(59, 130, 246, 0.15);
        border-left: 5px solid #3b82f6;
        color: #1d4ed8;
    }
    .badge {
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    .badge-3 { background-color: #ef4444; color: white; }
    .badge-2 { background-color: #f59e0b; color: white; }
    .badge-1 { background-color: #3b82f6; color: white; }
</style>
""", unsafe_allow_html=True)

# Título e Introdução
st.title("🚦 Simulador de Filas de Prioridade")
st.caption("Demonstração visual do comportamento de filas estritas (Prioridade 3 > Prioridade 2 > Prioridade 1) com perfis probabilísticos de entrada.")

# --- BARRA LATERAL: ENTRADA DE PARÂMETROS ---
st.sidebar.header("⚙️ Parâmetros da Simulação")

total_elementos = st.sidebar.slider(
    "Quantidade de elementos na fila:",
    min_value=5,
    max_value=100,
    value=20,
    step=1
)

st.sidebar.subheader("Distribuição Desejada (%)")
pct_p3 = st.sidebar.number_input("Prioridade 3 (Alta) %", min_value=0.0, max_value=100.0, value=30.0, step=5.0)
pct_p2 = st.sidebar.number_input("Prioridade 2 (Média) %", min_value=0.0, max_value=100.0, value=30.0, step=5.0)
pct_p1 = st.sidebar.number_input("Prioridade 1 (Baixa) %", min_value=0.0, max_value=100.0, value=40.0, step=5.0)

soma_pesos = pct_p3 + pct_p2 + pct_p1

if soma_pesos <= 0:
    st.sidebar.error("A soma das probabilidades deve ser maior que 0%.")
    st.stop()

# Normalização de pesos
peso_3 = (pct_p3 / soma_pesos) * 100
peso_2 = (pct_p2 / soma_pesos) * 100
peso_1 = (pct_p1 / soma_pesos) * 100

st.sidebar.info(
    f"**Perfil Normalizado:**\n"
    f"- P3: `{peso_3:.1f}%`\n"
    f"- P2: `{peso_2:.1f}%`\n"
    f"- P1: `{peso_1:.1f}%`"
)

usar_semente = st.sidebar.checkbox("Fixar semente aleatória (reprodutibilidade)", value=False)
semente = st.sidebar.number_input("Semente (Seed)", value=42, step=1) if usar_semente else None

executar = st.sidebar.button("🎲 Executar / Re-simular", type="primary")

# --- LÓGICA DE PROCESSAMENTO ---
if usar_semente and semente is not None:
    random.seed(int(semente))

# 1. Geração da fila de entrada
opcoes_prioridade = [3, 2, 1]
pesos = [peso_3, peso_2, peso_1]
prioridades_sorteadas = random.choices(opcoes_prioridade, weights=pesos, k=total_elementos)

fila_entrada = [
    {"posicao": i + 1, "id": f"P-{i+1:03d}", "prioridade": prioridades_sorteadas[i]}
    for i in range(total_elementos)
]

# 2. Distribuição para os deques de prioridade
filas_prioridade = {3: deque(), 2: deque(), 1: deque()}
for item in fila_entrada:
    filas_prioridade[item["prioridade"]].append(item)

# 3. Processamento estrito (3 > 2 > 1)
fila_processada = []
passo = 1
while any(len(f) > 0 for f in filas_prioridade.values()):
    if len(filas_prioridade[3]) > 0:
        atendido = dict(filas_prioridade[3].popleft())
        motivo = "Prioridade Máxima (3)"
    elif len(filas_prioridade[2]) > 0:
        atendido = dict(filas_prioridade[2].popleft())
        motivo = "Prioridade Média (2)"
    elif len(filas_prioridade[1]) > 0:
        atendido = dict(filas_prioridade[1].popleft())
        motivo = "Prioridade Baixa (1)"

    atendido["ordem_atendimento"] = passo
    atendido["motivo"] = motivo
    fila_processada.append(atendido)
    passo += 1

# --- RESUMO E MÉTRICAS ---
st.subheader("📊 Distribuição Amostrada vs. Teórica")
c1, c2, c3, c4 = st.columns(4)

total_p3 = sum(1 for x in fila_entrada if x["prioridade"] == 3)
total_p2 = sum(1 for x in fila_entrada if x["prioridade"] == 2)
total_p1 = sum(1 for x in fila_entrada if x["prioridade"] == 1)

c1.metric("Total de Elementos", total_elementos)
c2.metric("Prioridade 3 (Alta)", f"{total_p3} ({total_p3/total_elementos*100:.1f}%)", f"Esperado: {peso_3:.1f}%")
c3.metric("Prioridade 2 (Média)", f"{total_p2} ({total_p2/total_elementos*100:.1f}%)", f"Esperado: {peso_2:.1f}%")
c4.metric("Prioridade 1 (Baixa)", f"{total_p1} ({total_p1/total_elementos*100:.1f}%)", f"Esperado: {peso_1:.1f}%")

st.markdown("---")

# --- VISUALIZAÇÃO LADO A LADO ---
st.subheader("🔄 Visualização Comparativa das Filas")

col_esq, col_dir = st.columns(2)

def formatar_card(item, eh_saida=False):
    p = item["prioridade"]
    texto_prio = "Alta" if p == 3 else ("Média" if p == 2 else "Baixa")
    ordem_txt = f"#{item['ordem_atendimento']:02d}" if eh_saida else f"#{item['posicao']:02d}"
    return f"""
    <div class="item-card prio-{p}">
        <span><strong>{ordem_txt}</strong> &nbsp; | &nbsp; {item['id']}</span>
        <span class="badge badge-{p}">Prioridade {p} ({texto_prio})</span>
    </div>
    """

with col_esq:
    st.markdown("### 📥 Fila de Entrada (Ordem de Chegada)")
    st.caption("Ordem natural em que os itens chegaram ao sistema.")
    with st.container(height=520):
        for item in fila_entrada:
            st.markdown(formatar_card(item, eh_saida=False), unsafe_allow_html=True)

with col_dir:
    st.markdown("### 📤 Fila Processada (Ordem de Atendimento)")
    st.caption("Ordem final de consumo respeitando a política 3 > 2 > 1.")
    with st.container(height=520):
        for item in fila_processada:
            st.markdown(formatar_card(item, eh_saida=True), unsafe_allow_html=True)

# --- TABELA DETALHADA ---
st.markdown("---")
st.subheader("📋 Tabela Lado a Lado")

df_comparativo = pd.DataFrame({
    "Ordem": [f"#{i+1:02d}" for i in range(total_elementos)],
    "Entrada (ID)": [item["id"] for item in fila_entrada],
    "Entrada (Prioridade)": [f"P{item['prioridade']}" for item in fila_entrada],
    "Processado (ID)": [item["id"] for item in fila_processada],
    "Processado (Prioridade)": [f"P{item['prioridade']}" for item in fila_processada],
    "Motivo Atendimento": [item["motivo"] for item in fila_processada]
})

st.dataframe(df_comparativo, use_container_width=True, hide_index=True)