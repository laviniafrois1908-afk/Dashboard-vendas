import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import date

# -----------------------------
# Configuração da página
# -----------------------------
st.set_page_config(
    page_title="Dashboard de Vendas • Lavínia Fróis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# CSS (tema roxo escuro premium)
# -----------------------------
CSS = """
<style>
:root{
  --bg: #0b0b14;
  --panel: rgba(255,255,255,.06);
  --panel2: rgba(255,255,255,.08);
  --stroke: rgba(255,255,255,.10);
  --text: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.65);
  --accent: #8B5CF6;
  --accent2: #22D3EE;
  --good: #34D399;
  --warn: #FBBF24;
  --bad: #FB7185;
  --shadow: 0 12px 34px rgba(0,0,0,.38);
  --radius: 18px;
}
html, body, [class*="css"]{
  background: radial-gradient(1200px 700px at 12% 10%, rgba(139,92,246,.25), transparent 45%),
              radial-gradient(900px 600px at 90% 30%, rgba(34,211,238,.16), transparent 55%),
              radial-gradient(900px 700px at 50% 110%, rgba(139,92,246,.16), transparent 55%),
              var(--bg) !important;
  color: var(--text) !important;
}
.block-container{ padding-top: 1.2rem; padding-bottom: 1.5rem; }
[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
  border-right: 1px solid var(--stroke);
}
h1,h2,h3{ letter-spacing: -0.3px; }
.small-muted{ color: var(--muted); font-size: 0.95rem; }
.badge{
  display:inline-flex; align-items:center; gap:.45rem;
  padding:.35rem .6rem; border-radius: 999px;
  border:1px solid var(--stroke); background: rgba(255,255,255,.05);
  color: var(--muted); font-size:.88rem;
}
.hero{
  padding: 18px 18px;
  border-radius: var(--radius);
  background: linear-gradient(135deg, rgba(139,92,246,.22), rgba(34,211,238,.10));
  border: 1px solid rgba(255,255,255,.12);
  box-shadow: var(--shadow);
}
.hero-title{
  font-size: 2.0rem;
  margin: 0;
}
.hero-sub{
  margin-top: 6px;
  color: var(--muted);
}
.grid{ display:grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
@media (max-width: 1200px){
  .grid{ grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 650px){
  .grid{ grid-template-columns: 1fr; }
}
.card{
  border-radius: var(--radius);
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
  box-shadow: 0 10px 26px rgba(0,0,0,.28);
  padding: 14px 14px;
}
.card .label{ color: var(--muted); font-size: .92rem; }
.card .value{ font-size: 1.55rem; font-weight: 700; margin-top: 2px; }
.card .delta{ margin-top: 6px; color: var(--muted); font-size: .9rem; }
.hr{
  height: 1px; width: 100%;
  background: rgba(255,255,255,.10);
  margin: 12px 0 14px;
}
.stButton>button{
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.14);
  background: linear-gradient(135deg, rgba(139,92,246,.90), rgba(34,211,238,.70));
  color: #0b0b14;
  font-weight: 700;
  box-shadow: 0 10px 22px rgba(0,0,0,.25);
}
.stDownloadButton>button{
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.08);
  color: var(--text);
}
[data-testid="stMetricValue"]{ color: var(--text); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def fmt_brl(x: float) -> str:
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["cidade"] = df["cidade"].astype(str).str.strip()
    df["produto"] = df["produto"].astype(str).str.strip()
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0).astype(int)
    df["preco_unit"] = pd.to_numeric(df["preco_unit"], errors="coerce")
    df = df.dropna(subset=["data", "preco_unit"])
    df["total"] = df["quantidade"] * df["preco_unit"]
    return df

# -----------------------------
# Carregar dados
# -----------------------------
st.sidebar.title("⚙️ Controles")

fonte = st.sidebar.radio(
    "Fonte de dados",
    ["Usar vendas.csv", "Enviar meu CSV"],
    index=0
)

if fonte == "Enviar meu CSV":
    up = st.sidebar.file_uploader("Envie um CSV com colunas: data,cidade,produto,quantidade,preco_unit", type=["csv"])
    if up is None:
        st.stop()
    df = pd.read_csv(up)
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["cidade"] = df["cidade"].astype(str).str.strip()
    df["produto"] = df["produto"].astype(str).str.strip()
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce").fillna(0).astype(int)
    df["preco_unit"] = pd.to_numeric(df["preco_unit"], errors="coerce")
    df = df.dropna(subset=["data", "preco_unit"])
    df["total"] = df["quantidade"] * df["preco_unit"]
else:
    df = load_data("vendas.csv")

if df.empty:
    st.error("Seu dataset está vazio ou com colunas inválidas.")
    st.stop()

# -----------------------------
# Sidebar: filtros
# -----------------------------
min_d = df["data"].min().date()
max_d = df["data"].max().date()

periodo = st.sidebar.date_input(
    "Período",
    value=(min_d, max_d),
    min_value=min_d,
    max_value=max_d
)

if isinstance(periodo, tuple) and len(periodo) == 2:
    d0, d1 = periodo
else:
    d0, d1 = min_d, max_d

cidades = sorted(df["cidade"].unique().tolist())
produtos = sorted(df["produto"].unique().tolist())

sel_cidades = st.sidebar.multiselect("Cidades", cidades, default=cidades)
sel_produtos = st.sidebar.multiselect("Produtos", produtos, default=produtos)

df_f = df[
    (df["data"].dt.date >= d0) &
    (df["data"].dt.date <= d1) &
    (df["cidade"].isin(sel_cidades)) &
    (df["produto"].isin(sel_produtos))
].copy()

# -----------------------------
# Cabeçalho (Hero)
# -----------------------------
st.markdown(
    f"""
    <div class="hero">
      <div class="badge">✨ Python • Streamlit • Plotly</div>
      <h1 class="hero-title">Dashboard de Vendas</h1>
      <div class="hero-sub">Período filtrado: <b>{d0.strftime('%d/%m/%Y')}</b> até <b>{d1.strftime('%d/%m/%Y')}</b> • Registros: <b>{len(df_f)}</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -----------------------------
# KPIs
# -----------------------------
faturamento = float(df_f["total"].sum())
itens = int(df_f["quantidade"].sum())
num_vendas = int(len(df_f))
ticket = faturamento / num_vendas if num_vendas else 0.0

top_prod = df_f.groupby("produto", as_index=False)["total"].sum().sort_values("total", ascending=False)
top_city = df_f.groupby("cidade", as_index=False)["total"].sum().sort_values("total", ascending=False)

k1 = fmt_brl(faturamento)
k2 = f"{itens}"
k3 = f"{num_vendas}"
k4 = fmt_brl(ticket)

st.markdown(
    f"""
    <div class="grid">
      <div class="card">
        <div class="label">Faturamento</div>
        <div class="value">{k1}</div>
        <div class="delta">Soma de <b>quantidade × preço</b> no período</div>
      </div>
      <div class="card">
        <div class="label">Itens vendidos</div>
        <div class="value">{k2}</div>
        <div class="delta">Total de unidades vendidas</div>
      </div>
      <div class="card">
        <div class="label">Registros</div>
        <div class="value">{k3}</div>
        <div class="delta">Linhas do dataset filtrado</div>
      </div>
      <div class="card">
        <div class="label">Ticket médio</div>
        <div class="value">{k4}</div>
        <div class="delta">Faturamento / registros</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# -----------------------------
# Abas
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📈 Visão Geral", "🏙️ Cidades", "📦 Produtos"])

# Visão geral
with tab1:
    df_time = (
    df_f.assign(data=df_f["data"].dt.date)
      .groupby("data", as_index=False)["total"]
      .sum()
)


    fig_line = px.line(df_time, x="data", y="total", markers=True, title="Faturamento por dia")
    fig_line.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,.88)"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=55, b=10)
    )
    fig_line.update_xaxes(showgrid=False)
    fig_line.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,.08)")
    st.plotly_chart(fig_line, use_container_width=True)

    st.markdown("#### 🧾 Tabela (dados filtrados)")
    st.dataframe(
        df_f.sort_values("data", ascending=False),
        use_container_width=True,
        hide_index=True
    )

# Cidades
with tab2:
    fig_city = px.bar(
        top_city.head(12),
        x="cidade",
        y="total",
        title="Faturamento por cidade (Top 12)",
    )
    fig_city.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,.88)"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=55, b=10)
    )
    fig_city.update_xaxes(showgrid=False)
    fig_city.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,.08)")
    st.plotly_chart(fig_city, use_container_width=True)

    st.markdown("#### Ranking completo")
    st.dataframe(top_city, use_container_width=True, hide_index=True)

# Produtos
with tab3:
    fig_prod = px.bar(
        top_prod.head(12),
        x="produto",
        y="total",
        title="Faturamento por produto (Top 12)",
    )
    fig_prod.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,.88)"),
        title_font=dict(size=18),
        margin=dict(l=10, r=10, t=55, b=10)
    )
    fig_prod.update_xaxes(showgrid=False)
    fig_prod.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,.08)")
    st.plotly_chart(fig_prod, use_container_width=True)

    st.markdown("#### Ranking completo")
    st.dataframe(top_prod, use_container_width=True, hide_index=True)

# -----------------------------
# Downloads
# -----------------------------
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

colA, colB, colC = st.columns([1.2, 1.2, 2.6])

with colA:
    st.download_button(
        "⬇️ Baixar dados filtrados (CSV)",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="dados_filtrados.csv",
        mime="text/csv"
    )

with colB:
    resumo = pd.DataFrame({
        "kpi": ["Faturamento", "Itens", "Registros", "Ticket médio"],
        "valor": [fmt_brl(faturamento), itens, num_vendas, fmt_brl(ticket)]
    })
    st.download_button(
        "⬇️ Baixar resumo (CSV)",
        data=resumo.to_csv(index=False).encode("utf-8"),
        file_name="resumo_kpis.csv",
        mime="text/csv"
    )

with colC:
    st.markdown(
        "<div class='small-muted'>💡 Dica de portfólio: no README, coloque prints do dashboard e explique os KPIs, filtros e limpeza de dados.</div>",
        unsafe_allow_html=True
    )
