import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Pro Financial Annuities", layout="wide")

# Refined Professional Aesthetics (Dark Mode Compatible)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Titles & Subtitles */
    .main-title { 
        color: var(--text-color);
        font-weight: 800; 
        text-align: left; 
        font-size: 2.2rem; 
        letter-spacing: -1.5px;
        margin-bottom: 0rem;
    }
    
    .subtitle { 
        text-align: left; 
        color: #64748b; 
        margin-bottom: 1.5rem; 
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 400;
    }

    /* Metric Cards adapted for Dark/Light */
    .metric-card { 
        background: rgba(120, 150, 180, 0.05); 
        padding: 24px; 
        border-radius: 12px; 
        border: 1px solid rgba(120, 150, 180, 0.2);
        text-align: left;
    }
    
    /* COMPACT SUMMARY BAR (Translucent for Dark Mode) */
    .summary-bar {
        background: rgba(120, 150, 180, 0.08);
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        border: 1px solid rgba(120, 150, 180, 0.15);
    }

    .summary-item { text-align: center; }

    .summary-label {
        color: #94a3b8;
        font-size: 0.6rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: -2px;
    }

    .summary-value {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--text-color);
    }

    .label { 
        color: #94a3b8; 
        font-size: 0.7rem; 
        font-weight: 600; 
        text-transform: uppercase; 
        letter-spacing: 0.5px;
    }
    
    .value { 
        font-size: 1.6rem; 
        font-weight: 700; 
        display: block; 
        margin-top: 4px; 
        color: var(--text-color);
    }
    
    .blue-v { color: #3b82f6; }
    .green-v { color: #10b981; }
    .red-v { color: #ef4444; }

    /* Number Input fix for visibility */
    .stNumberInput div div input {
        padding-top: 2px !important;
        padding-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. CALCULATION ENGINE ---
def calcular_simulacion(principal, renta_m, tasa_a, reval, infla, años, diferimiento):
    nominal, real, rentas = [principal], [principal], []
    tasa = tasa_a / 100
    renta_act = renta_m * 12
    
    for t in range(1, años + 1):
        intereses = nominal[-1] * tasa
        pago_renta = 0 if t <= diferimiento else renta_act
        
        nuevo_saldo = max(0, nominal[-1] + intereses - pago_renta)
        nominal.append(nuevo_saldo)
        rentas.append(pago_renta)
        
        if t > diferimiento:
            renta_act *= (1 + reval)
            
        real.append(nuevo_saldo / ((1 + infla) ** t))
    return nominal, real, rentas

def buscar_extincion(principal, renta_m, tasa_a, reval, diferimiento):
    if principal <= 0: return 0
    if renta_m <= 0: return float('inf')
    
    s, r, t = principal, renta_m * 12, tasa_a / 100
    mes_inicio_cobro = diferimiento * 12
    
    for mes in range(1, 1201):
        interes_mes = s * (t/12)
        pago_mes = 0 if mes <= mes_inicio_cobro else (r/12)
        s = s + interes_mes - pago_mes
        
        if mes > mes_inicio_cobro and mes % 12 == 0:
            r *= (1 + reval)
            
        if s <= 0: return mes / 12
    return float('inf')

# --- 3. COMPRESSED SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    
    with st.expander("💰 Capital & Income", expanded=True):
        cap = st.number_input("Initial Balance (€)", value=0.0, step=1000.0)
        ren = st.number_input("Monthly Income (€)", value=0.0, step=100.0)
        dif = st.number_input("Deferment Years", min_value=0, max_value=20, value=0, step=1)
    
    with st.expander("📈 Adjust Hypotheses", expanded=False):
        tasa = st.slider("Return Rate (%)", 0.0, 10.0, 4.0, step=0.25)
        inf_val = st.slider("Inflation (%)", 0.0, 5.0, 2.0, step=0.25)
        inf = inf_val / 100
        rev_val = st.slider("Income Reval. (%)", 0.0, 5.0, 0.0, step=0.25)
        rev = rev_val / 100
    
    with st.expander("🔍 Target Year Detail", expanded=False):
        años_max = 30 
        año_objetivo = st.slider("Selected Year:", 1, años_max, 20)

# --- 4. CALCULATIONS ---
nom, real, _ = calcular_simulacion(cap, ren, tasa, rev, inf, años_max, dif)
ext = buscar_extincion(cap, ren, tasa, rev, dif)

if cap == 0 and ren == 0:
    ext_txt = "0 years"
else:
    ext_txt = f"{int(ext)} years and {int((ext-int(ext))*12)} months" if ext != float('inf') else "Perpetual"

# --- 5. MAIN INTERFACE ---
st.markdown('<h1 class="main-title">Financial Annuities <span style="color:#3b82f6">Pro</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Pension Plan Drawdown Simulation</p>', unsafe_allow_html=True)

# SIDEBAR DATA SUMMARY (COMPACT)
st.markdown(f"""
    <div class="summary-bar">
        <div class="summary-item"><p class="summary-label">Capital</p><p class="summary-value">{cap:,.0f} €</p></div>
        <div class="summary-item"><p class="summary-label">Income</p><p class="summary-value">{ren:,.0f} €/m</p></div>
        <div class="summary-item"><p class="summary-label">Waiting</p><p class="summary-value">{dif} years</p></div>
        <div class="summary-item"><p class="summary-label">Return</p><p class="summary-value">{tasa}%</p></div>
        <div class="summary-item"><p class="summary-label">CPI</p><p class="summary-value">{inf_val}%</p></div>
        <div class="summary-item"><p class="summary-label">Reval.</p><p class="summary-value">{rev_val}%</p></div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><span class="label">Capital Depletion</span><span class="value red-v">{ext_txt}</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><span class="label">Nominal Balance (Year {año_objetivo})</span><span class="value blue-v">{nom[año_objetivo]:,.0f} €</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><span class="label">Purchasing Power (Year {año_objetivo})</span><span class="value green-v">{real[año_objetivo]:,.0f} €</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_viz, col_data = st.columns([2, 1], gap="large")

with col_viz:
    st.markdown("#### Portfolio Evolution")
    fig = go.Figure()
    años_x = list(range(años_max + 1))
    
    fig.add_trace(go.Scatter(
        x=años_x, y=nom, name="Nominal Balance", 
        line=dict(width=3, color='#3b82f6'),
        hovertemplate='%{y:,.0f} €'
    ))
    
    fig.add_trace(go.Scatter(
        x=años_x, y=real, name="Real Value (CPI Adjusted)", 
        fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)',
        line=dict(width=2, color='#10b981', dash='dot'),
        hovertemplate='%{y:,.0f} €'
    ))
    
    if dif > 0:
        fig.add_vrect(
            x0=0, x1=dif, fillcolor="gray", opacity=0.1, layer="below", line_width=0,
            annotation_text="Deferment", annotation_position="top left"
        )
    
    fig.add_vline(x=año_objetivo, line_dash="dash", line_color="#64748b")
    
    fig.update_layout(
        template="plotly_dark" if st.get_option("theme.base") == "dark" else "plotly_white",
        hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=400, margin=dict(l=0, r=0, t=10, b=0), 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='rgba(120, 150, 180, 0.1)', title="Years"),
        yaxis=dict(showgrid=True, gridcolor='rgba(120, 150, 180, 0.1)', tickformat=",.0f", title="Capital (€)")
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_data:
    st.markdown(f"#### Scenarios at Year {año_objetivo}")
    variaciones = [-1.0, -0.5, 0, 0.5, 1.0]
    tabla_datos = []
    for v in variaciones:
        t_v = tasa + v
        if t_v < 0: continue
        n_v, r_v, _ = calcular_simulacion(cap, ren, t_v, rev, inf, años_max, dif)
        ex_v = buscar_extincion(cap, ren, t_v, rev, dif)
        dur = f"{int(ex_v)}y" if ex_v != float('inf') else "Perp."
        tabla_datos.append({
            "Return": f"{t_v:.1f}%", "Duration": dur,
            "Nominal": f"{n_v[año_objetivo]:,.0f} €", "Real": f"{r_v[año_objetivo]:,.0f} €"
        })

    st.dataframe(pd.DataFrame(tabla_datos), use_container_width=True, hide_index=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("Wealth Optimizer — Wealth Analysis Terminal")
