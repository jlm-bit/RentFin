import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rentas Financieras Pro", layout="wide")
 
# Estética Profesional Refinada
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #ffffff;
    }

    .stApp { background-color: #ffffff; }
    
    .main-title { 
        color: #0f172a;
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

    .metric-card { 
        background: #f8fafc; 
        padding: 24px; 
        border-radius: 12px; 
        border: 1px solid #f1f5f9;
        text-align: left;
    }
    
    /* RESUMEN COMPACTO */
    .summary-bar {
        background: #f8fafc;
        padding: 10px 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        border: 1px solid #e2e8f0;
    }

    .summary-item {
        text-align: center;
    }

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
        color: #334155;
    }

    .label { 
        color: #64748b; 
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
        color: #1e293b;
    }
    
    .blue-v { color: #2563eb; }
    .green-v { color: #10b981; }
    .red-v { color: #f43f5e; }

    [data-testid="stSidebar"] {
        background-color: #f1f5f9;
        border-right: 1px solid #e2e8f0;
    }
    
    .stNumberInput div div input {
        padding-top: 2px !important;
        padding-bottom: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOTOR DE CÁLCULO ---
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

# --- 3. SIDEBAR COMPRIMIDO ---
with st.sidebar:
    st.markdown("### ⚙️ Configuración")
    
    with st.expander("💰 Capital y Rentas", expanded=True):
        cap = st.number_input("Saldo inicial (€)", value=0.0, step=1000.0)
        ren = st.number_input("Renta mensual (€)", value=0.0, step=100.0)
        dif = st.number_input("Años diferimiento", min_value=0, max_value=20, value=0, step=1)
    
    with st.expander("📈 Modificar Hipotesis", expanded=False):
        tasa = st.slider("Rentabilidad (%)", 0.0, 10.0, 4.0, step=0.25)
        inf_val = st.slider("Inflación (%)", 0.0, 5.0, 2.0, step=0.25)
        inf = inf_val / 100
        rev_val = st.slider("Reval. Renta (%)", 0.0, 5.0, 0.0, step=0.25)
        rev = rev_val / 100
    
    with st.expander("🔍 Modificar Año de Detalle", expanded=False):
        años_max = 30 
        año_objetivo = st.slider("Año de detalle:", 1, años_max, 20)

# --- 4. CÁLCULOS ---
nom, real, _ = calcular_simulacion(cap, ren, tasa, rev, inf, años_max, dif)
ext = buscar_extincion(cap, ren, tasa, rev, dif)

if cap == 0 and ren == 0:
    ext_txt = "0 años"
else:
    ext_txt = f"{int(ext)} años y {int((ext-int(ext))*12)} meses" if ext != float('inf') else "Perpetuo"

# --- 5. INTERFAZ PRINCIPAL ---
st.markdown('<h1 class="main-title">Rentas financieras <span style="color:#2563eb">Pro</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Simulación de Disposición de tu Plan de Pensiones</p>', unsafe_allow_html=True)

# RESUMEN DE DATOS DEL SIDEBAR (MÁS PEQUEÑO)
st.markdown(f"""
    <div class="summary-bar">
        <div class="summary-item"><p class="summary-label">Capital</p><p class="summary-value">{cap:,.0f} €</p></div>
        <div class="summary-item"><p class="summary-label">Renta</p><p class="summary-value">{ren:,.0f} €/m</p></div>
        <div class="summary-item"><p class="summary-label">Espera</p><p class="summary-value">{dif} años</p></div>
        <div class="summary-item"><p class="summary-label">Rend.</p><p class="summary-value">{tasa}%</p></div>
        <div class="summary-item"><p class="summary-label">IPC</p><p class="summary-value">{inf_val}%</p></div>
        <div class="summary-item"><p class="summary-label">Reval.</p><p class="summary-value">{rev_val}%</p></div>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f'<div class="metric-card"><span class="label">Extinción del Capital</span><span class="value red-v">{ext_txt}</span></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><span class="label">Saldo Nominal (Año {año_objetivo})</span><span class="value blue-v">{nom[año_objetivo]:,.0f} €</span></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><span class="label">Poder Adquisitivo (Año {año_objetivo})</span><span class="value green-v">{real[año_objetivo]:,.0f} €</span></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col_viz, col_data = st.columns([2, 1], gap="large")

with col_viz:
    st.markdown("#### Evolución del Patrimonio")
    fig = go.Figure()
    años_x = list(range(años_max + 1))
    
    fig.add_trace(go.Scatter(
        x=años_x, y=nom, name="Saldo Nominal", 
        line=dict(width=3, color='#1e293b'),
        hovertemplate='%{y:,.0f} €'
    ))
    
    fig.add_trace(go.Scatter(
        x=años_x, y=real, name="Poder Real (Ajustado IPC)", 
        fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.05)',
        line=dict(width=2, color='#10b981', dash='dot'),
        hovertemplate='%{y:,.0f} €'
    ))
    
    if dif > 0:
        fig.add_vrect(
            x0=0, x1=dif, fillcolor="#f1f5f9", opacity=0.5, layer="below", line_width=0,
            annotation_text="Diferimiento", annotation_position="top left"
        )
    
    fig.add_vline(x=año_objetivo, line_dash="dash", line_color="#cbd5e1")
    
    fig.update_layout(
        hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=400, margin=dict(l=0, r=0, t=10, b=0), 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor='#f1f5f9', title="Años"),
        yaxis=dict(showgrid=True, gridcolor='#f1f5f9', tickformat=",.0f", title="Capital (€)")
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_data:
    st.markdown(f"#### Escenarios al Año {año_objetivo}")
    variaciones = [-1.0, -0.5, 0, 0.5, 1.0]
    tabla_datos = []
    for v in variaciones:
        t_v = tasa + v
        if t_v < 0: continue
        n_v, r_v, _ = calcular_simulacion(cap, ren, t_v, rev, inf, años_max, dif)
        ex_v = buscar_extincion(cap, ren, t_v, rev, dif)
        dur = f"{int(ex_v)}a" if ex_v != float('inf') else "Perp."
        tabla_datos.append({
            "Rend.": f"{t_v:.1f}%", "Duración": dur,
            "Nominal": f"{n_v[año_objetivo]:,.0f} €", "Real": f"{r_v[año_objetivo]:,.0f} €"
        })

    st.dataframe(pd.DataFrame(tabla_datos), use_container_width=True, hide_index=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.caption("Wealth Optimizer — Terminal de Análisis Patrimonial")
