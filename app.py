import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ================================================================
# CONFIGURACIÓN (Prácticas 2, 7)
# ================================================================
st.set_page_config(
    page_title="Radar ICFES — Visión por Dependencia",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* Responsive layout constraints */
    .main .block-container { padding-top: 1.5rem; max-width: 1400px; }
    
    /* Minimalist header */
    .dashboard-header {
        background: white;
        border-left: 6px solid #1A3A6B;
        padding: 1.5rem 2rem; 
        border-radius: 4px;
        margin-bottom: 2rem; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .dashboard-header h1 { margin: 0; font-weight: 700; font-size: 1.8rem; color: #1A1A2E; letter-spacing: -0.5px; }
    .dashboard-header p { margin: 0.3rem 0 0 0; color: #6B7280; font-size: 0.95rem; }
    
    /* Card design */
    .kpi-card {
        background: white; border: 1px solid #E5E7EB; border-radius: 8px;
        padding: 1.2rem; box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; justify-content: center; height: 100%;
    }
    .kpi-label { font-size: 0.8rem; font-weight: 600; color: #6B7280; text-transform: uppercase; margin-bottom: 0.3rem; }
    .kpi-value { font-size: 1.8rem; font-weight: 700; color: #111827; line-height: 1.1; }
    .kpi-subtext { font-size: 0.8rem; margin-top: 0.4rem; color: #6B7280; }
    .kpi-subtext.positive { color: #059669; font-weight: 500; }
    .kpi-subtext.negative { color: #DC2626; font-weight: 500; }
    
    /* Headers de secciones ultra-clean */
    .section-title {
        font-size: 1.15rem; font-weight: 600; color: #111827; 
        margin: 2.5rem 0 1rem 0; padding-bottom: 0.5rem; 
        border-bottom: 1px solid #E5E7EB;
    }
    
    /* Clean benchmark card */
    .benchmark-card {
        background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 6px;
        padding: 1rem; text-align: center;
    }
    .benchmark-card .bm-label { font-size: 0.75rem; font-weight: 600; color: #475569; text-transform: uppercase; }
    .benchmark-card .bm-value { font-size: 1.3rem; font-weight: 700; color: #1E293B; margin: 0.3rem 0; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Práctica 5: Limitar colores
COLORS = {
    'azul': '#1A3A6B',     # Principal Abastecimiento
    'verde': '#059669',    # Positivo / Ahorro / A tiempo
    'rojo': '#DC2626',     # Negativo / Sobrecosto / Retraso
    'gris': '#CBD5E1',     # Otras áreas / Base
    'grid': '#F3F4F6'
}

PLOTLY_TEMPLATE = 'plotly_white'
OPCION_GLOBAL = '🌍 Visión Global (Todo el ICFES)'

def fmt_cop(valor):
    if pd.isna(valor): return "N/A"
    if abs(valor) >= 1e9: return f"${valor/1e9:,.1f} MM"
    elif abs(valor) >= 1e6: return f"${valor/1e6:,.1f} M"
    else: return f"${valor:,.0f}"

def kpi_card(label, value, subtext=None, state="neutral", tooltip=None):
    subtext_html = f'<div class="kpi-subtext {state}">{subtext}</div>' if subtext else ""
    st.markdown(f'''
    <div class="kpi-card" {"title='"+tooltip+"'" if tooltip else ""}>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {subtext_html}
    </div>''', unsafe_allow_html=True)

# ================================================================
# DATOS (Práctica 3)
# ================================================================
@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), 'Base_Cruzada_Maestra_24_25.xlsx')
    if not os.path.exists(ruta):
        return pd.DataFrame()
        
    df = pd.read_excel(ruta, sheet_name='Maestra_24_25', engine='openpyxl')
    
    # Validar y castear
    cols_numericas = ['CONTRATO_Valor', 'CONTRATO_Valor_Inicial', 'Valor_Esperado_PAA', 
                      'KPI_Dias_Desfase', 'KPI_Desviacion_Valor', 'KPI_Crecimiento_Contractual']
    cols_texto = ['CONTRATO_Area', 'CONTRATO_Estado', 'CONTRATO_Referencia', 'CONTRATO_Objeto', 
                  'CONTRATO_Nombre_Contratista', 'urlproceso']
                  
    for col in cols_numericas:
        if col not in df.columns: df[col] = 0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    for col in cols_texto:
        if col not in df.columns: df[col] = 'No Registra'
        df[col] = df[col].astype(str).str.strip().replace('nan', 'No Registra')
        
    df['Annio_PAA'] = pd.to_numeric(df.get('Annio_PAA', 0), errors='coerce').fillna(0).astype('Int64')
    if 'CONTRATO_Fecha_Firma' in df.columns:
        df['CONTRATO_Fecha_Firma'] = pd.to_datetime(df['CONTRATO_Fecha_Firma'], errors='coerce')
    else:
        df['CONTRATO_Fecha_Firma'] = pd.NaT
        
    df['CONTRATO_Estado'] = df['CONTRATO_Estado'].str.capitalize()
    return df

df_all = cargar_datos()

if df_all.empty:
    st.error("No se encontró el archivo de datos 'Base_Cruzada_Maestra_24_25.xlsx'.")
    st.stop()

# Cache global stats to avoid recalculation
@st.cache_data
def get_global_stats(df_full):
    return df_full.groupby('CONTRATO_Area').agg(
        Contratos=('CONTRATO_Referencia', 'count'),
        Valor_Total=('CONTRATO_Valor', 'sum'),
        Desviacion_Neta=('KPI_Desviacion_Valor', 'sum'),
        Desfase_Promedio=('KPI_Dias_Desfase', 'mean')
    ).reset_index()

area_stats_global = get_global_stats(df_all)

# ================================================================
# SIDEBAR
# ================================================================
dependencias = sorted([area for area in df_all['CONTRATO_Area'].unique() if pd.notna(area) and area != 'No Registra'])
opciones_dependencia = [OPCION_GLOBAL] + dependencias

area_seleccionada = st.sidebar.selectbox("🔍 Seleccionar Dependencia", opciones_dependencia)
st.sidebar.markdown('---')

if area_seleccionada == OPCION_GLOBAL:
    df_base = df_all.copy()
else:
    df_base = df_all[df_all['CONTRATO_Area'] == area_seleccionada].copy()

years = sorted([y for y in df_base['Annio_PAA'].unique() if y != 0])
sel_years = st.sidebar.multiselect("Vigencia", years, default=years)

estados = sorted(df_base['CONTRATO_Estado'].unique())
sel_estados = st.sidebar.multiselect("Estado del Contrato", estados, default=estados)

df = df_base[
    (df_base['Annio_PAA'].isin(sel_years)) &
    (df_base['CONTRATO_Estado'].isin(sel_estados))
].copy()

# ================================================================
# HEADER
# ================================================================
st.markdown(f"""
<div class="dashboard-header">
    <h1>{area_seleccionada if area_seleccionada != OPCION_GLOBAL else 'Visión Global del ICFES'}</h1>
    <p>Dashboard Analítico  |  Última evaluación: 2025</p>
</div>
""", unsafe_allow_html=True)

if len(df) == 0:
    st.warning("⚠️ No hay datos con los filtros seleccionados.")
    st.stop()

# ================================================================
# 01. KPIs (Práctica 1 y 4: Zona Óptima e Info Clave)
# ================================================================
total = len(df)
valor_total = df['CONTRATO_Valor'].sum()
desv_neta = df['KPI_Desviacion_Valor'].sum()
desfase_prom = df['KPI_Dias_Desfase'].mean()
n_contratistas = df['CONTRATO_Nombre_Contratista'].nunique()

c1, c2, c3, c4 = st.columns(4)

with c1:
    kpi_card("Contratación Total", fmt_cop(valor_total), 
             f"{total} contratos firmados", "neutral", 
             tooltip="Valor total comprometido en los contratos filtrados")
with c2:
    if abs(desv_neta) < 1000:
        kpi_card("Desviación vs PAA", "Sin Desviación", "Dentro del presupuesto planeado")
    else:
        estado = "Ahorro" if desv_neta < 0 else "Sobrecosto"
        color = "positive" if desv_neta < 0 else "negative"
        kpi_card("Desviación vs PAA", fmt_cop(abs(desv_neta)), f"Neto en {estado}", color,
                 tooltip="Diferencia financiera total entre el valor PAA planeado inicial y el valor real del contrato actual")
with c3:
    color_desf = "positive" if desfase_prom <= 15 else "negative"
    kpi_card("Retraso de Firma", f"{desfase_prom:.0f} días" if not pd.isna(desfase_prom) else "N/D", 
             "Promedio vs fecha PAA", color_desf,
             tooltip="Diferencia en días entre la fecha en que se planeaba firmar (PAA) y la fecha de firma electrónica real")
with c4:
    kpi_card("Base Proveedores", f"{n_contratistas}", "Contratistas únicos gestionados", "neutral")

# ================================================================
# 02. DESEMPEÑO FINANCIERO (Prácticas 8 y 9)
# ================================================================
st.markdown('<div class="section-title">Desempeño Financiero: Planeación vs Realidad</div>', unsafe_allow_html=True)

col_fin1, col_fin2 = st.columns(2)

with col_fin1:
    # Evolución Planeado VS Real
    fin = df.groupby('Annio_PAA').agg(
        Valor_Real=('CONTRATO_Valor','sum'), Desviacion=('KPI_Desviacion_Valor','sum')
    ).reset_index()
    fin['Planeado'] = fin['Valor_Real'] - fin['Desviacion']
    fm = fin.melt(id_vars='Annio_PAA', value_vars=['Planeado','Valor_Real'], var_name='Tipo', value_name='Valor')
    
    fig = px.bar(fm, x='Annio_PAA', y='Valor', color='Tipo', barmode='group',
                 color_discrete_map={'Planeado': COLORS['azul'], 'Valor_Real': COLORS['gris']},
                 text_auto='.2s', template=PLOTLY_TEMPLATE)
                 
    # Usar tooltips ricos (Práctica 8)
    fig.update_traces(
        hovertemplate="<br>".join([
            "<b>%{x}</b>",
            "%{data.name}: $%{y:,.0f}",
            "<extra></extra>"
        ])
    )
    fig.update_layout(
        xaxis_title="", yaxis_title="", 
        legend_title="", legend=dict(orientation="h", y=1.1, x=0),
        xaxis=dict(tickmode='array', tickvals=years), yaxis=dict(showticklabels=False),
        margin=dict(l=0, r=0, t=10, b=0) # Práctica 9: Eliminar desorden
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

with col_fin2:
    # Top Sobrecostos con Custom Tooltips
    top = df[df['KPI_Desviacion_Valor'] > 0].nlargest(8, 'KPI_Desviacion_Valor')
    if not top.empty:
        # Práctica 8: Historias en Tooltips
        top['Tooltip'] = top.apply(lambda r: (
            f"<b>{r['CONTRATO_Referencia']}</b><br>"
            f"Contratista: {r['CONTRATO_Nombre_Contratista'][:40]}...<br>"
            f"Objeto: {r['CONTRATO_Objeto'][:80]}...<br><br>"
            f"Valor PAA: {fmt_cop(r['Valor_Esperado_PAA'])}<br>"
            f"Valor Real: {fmt_cop(r['CONTRATO_Valor'])}<br>"
            f"Sobrecosto: {fmt_cop(r['KPI_Desviacion_Valor'])}"
        ), axis=1)

        fig = px.bar(top, y='CONTRATO_Referencia', x='KPI_Desviacion_Valor', orientation='h',
                     custom_data=['Tooltip'], template=PLOTLY_TEMPLATE, text_auto='.2s')
                     
        fig.update_traces(
            marker_color=COLORS['rojo'], 
            hovertemplate="%{customdata[0]}<extra></extra>",
            textposition='outside'
        )
        fig.update_layout(
            xaxis_title="", yaxis_title="", 
            yaxis={'categoryorder':'total ascending'}, xaxis=dict(showticklabels=False),
            margin=dict(l=0, r=0, t=10, b=0),
            title=dict(text="Top Mayores Desviaciones ($)", font=dict(size=14, color='#4B5563'))
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Sin registros con sobrecosto o adiciones para el filtro actual.")

# ================================================================
# 03. OPORTUNIDAD Y CONCENTRACIÓN (Práctica 5, reduciendo charts)
# ================================================================
c_op1, c_op2 = st.columns([1, 1])

with c_op1:
    st.markdown('<div class="section-title">Oportunidad Contractual</div>', unsafe_allow_html=True)
    df_mes = df[df['CONTRATO_Fecha_Firma'].notna() & df['KPI_Dias_Desfase'].notna()].copy()
    if not df_mes.empty:
        df_mes['Mes'] = df_mes['CONTRATO_Fecha_Firma'].dt.month
        df_mes['Puntualidad'] = np.where(df_mes['KPI_Dias_Desfase']<=0, 'A tiempo', 'Retraso')
        
        # Combinar timing y estacionalidad en un chart apilado por mes
        mc = df_mes.groupby(['Mes', 'Puntualidad']).size().reset_index(name='Count')
        ml = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
        mc['Mes_Nombre'] = mc['Mes'].map(ml)
        
        fig = px.bar(mc, x='Mes_Nombre', y='Count', color='Puntualidad', 
                     color_discrete_map={'A tiempo': COLORS['verde'], 'Retraso': COLORS['rojo']},
                     category_orders={"Mes_Nombre": list(ml.values())}, template=PLOTLY_TEMPLATE)
        
        fig.update_layout(
            xaxis_title="", yaxis_title="Cantidad de Registros",
            legend_title="", legend=dict(orientation="h", y=1.1, x=0),
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No hay fechas exactas disponibles para medir oportunidad.")

with c_op2:
    st.markdown('<div class="section-title">Concentración Proveedores (Top)</div>', unsafe_allow_html=True)
    # Treemap en lugar de barras para máxima densidad visual
    top_prov = df.groupby('CONTRATO_Nombre_Contratista')['CONTRATO_Valor'].sum().reset_index()
    top_prov = top_prov[top_prov['CONTRATO_Valor'] > 0]
    top_prov = top_prov.nlargest(15, 'CONTRATO_Valor')
    
    if not top_prov.empty:
        top_prov['Tooltip_Val'] = top_prov['CONTRATO_Valor'].apply(fmt_cop)
        path_root = px.Constant(area_seleccionada[:30] if area_seleccionada != OPCION_GLOBAL else "ICFES")
        fig = px.treemap(top_prov, path=[path_root, 'CONTRATO_Nombre_Contratista'], 
                         values='CONTRATO_Valor', color='CONTRATO_Valor',
                         color_continuous_scale=[COLORS['gris'], COLORS['azul']],
                         custom_data=['Tooltip_Val'])
                         
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>Asignado: %{customdata[0]}<extra></extra>",
            textinfo="label+value"
        )
        fig.update_layout(margin=dict(t=0, l=0, r=0, b=0), coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No hay valores para dibujar treemap.")

# ================================================================
# 04. BENCHMARK
# ================================================================
if area_seleccionada != OPCION_GLOBAL:
    st.markdown('<div class="section-title">Ranking Institucional (Contexto ICFES)</div>', unsafe_allow_html=True)
    
    area_stats_sorted_val = area_stats_global.sort_values('Valor_Total', ascending=False).reset_index(drop=True)
    try:
        rank_val = area_stats_sorted_val[area_stats_sorted_val['CONTRATO_Area'] == area_seleccionada].index[0] + 1
    except IndexError:
        rank_val = "N/A"
    total_areas = len(area_stats_sorted_val)
    
    area_stats_sorted_desf = area_stats_global[area_stats_global['Desfase_Promedio'].notna()].sort_values('Desfase_Promedio').reset_index(drop=True)
    if area_seleccionada in area_stats_sorted_desf['CONTRATO_Area'].values:
        rank_desf = area_stats_sorted_desf[area_stats_sorted_desf['CONTRATO_Area'] == area_seleccionada].index[0] + 1
    else:
        rank_desf = "N/A"
    n_desf = len(area_stats_sorted_desf)
    
    pct_presup = (valor_total / area_stats_global['Valor_Total'].sum() * 100) if area_stats_global['Valor_Total'].sum()>0 else 0
    
    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Posición Presupuestal</div>
                    <div class="bm-value">#{rank_val} de {total_areas}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Maneja el {pct_presup:.1f}% de los recursos de la entidad.</div></div>''', unsafe_allow_html=True)
    with cb2:
        st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Posición en Oportunidad (Rapidez)</div>
                    <div class="bm-value">#{rank_desf} de {n_desf}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Basado en el desfase firma PAA vs Real.</div></div>''', unsafe_allow_html=True)
    with cb3:
        if abs(desv_neta) > 1000:
            c_ahorro = "#059669" if desv_neta < 0 else "#DC2626"
            lbl_ahorro = "Ahorró" if desv_neta < 0 else "Sobrecostó"
            pct_desv = (abs(desv_neta) / df['Valor_Esperado_PAA'].sum() * 100) if df['Valor_Esperado_PAA'].sum()>0 else 0
            st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Eficiencia vs Estimado</div>
                        <div class="bm-value" style="color:{c_ahorro};">{lbl_ahorro} {pct_desv:.1f}%</div>
                        <div style="font-size:0.8rem; color:#64748B;">En relación con el valor presupuestado.</div></div>''', unsafe_allow_html=True)
        else:
            st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Eficiencia vs Estimado</div>
                        <div class="bm-value" style="color:#059669;">Sin Desvío</div>
                        <div style="font-size:0.8rem; color:#64748B;">Alineado 100% con el PAA.</div></div>''', unsafe_allow_html=True)
else:
    # If it is the global vision, show completely different stats.
    st.markdown('<div class="section-title">Resumen Institucional (Top Dependencias)</div>', unsafe_allow_html=True)
    area_stats_sorted_val = area_stats_global.sort_values('Valor_Total', ascending=False).reset_index(drop=True)
    top_area_val = area_stats_sorted_val['CONTRATO_Area'].iloc[0] if not area_stats_sorted_val.empty else "N/A"
    top_val = area_stats_sorted_val['Valor_Total'].iloc[0] if not area_stats_sorted_val.empty else 0
    
    area_stats_sorted_desf = area_stats_global[area_stats_global['Desfase_Promedio'].notna()].sort_values('Desfase_Promedio', ascending=False).reset_index(drop=True)
    top_area_desf_negativo = area_stats_sorted_desf['CONTRATO_Area'].iloc[0] if not area_stats_sorted_desf.empty else "N/A"
    top_desf_negativo = area_stats_sorted_desf['Desfase_Promedio'].iloc[0] if not area_stats_sorted_desf.empty else 0
    
    cb1, cb2, cb3 = st.columns(3)
    with cb1:
        st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Mayor Presupuesto Ejecutado</div>
                    <div class="bm-value">{fmt_cop(top_val)}</div>
                    <div style="font-size:0.8rem; color:#64748B;">{top_area_val[:50]}...</div></div>''', unsafe_allow_html=True)
    with cb2:
        st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Mayor Retraso Promedio</div>
                    <div class="bm-value">{top_desf_negativo:.0f} días</div>
                    <div style="font-size:0.8rem; color:#64748B;">{top_area_desf_negativo[:50]}...</div></div>''', unsafe_allow_html=True)
    with cb3:
        st.markdown(f'''<div class="benchmark-card"><div class="bm-label">Dependencias Activas</div>
                    <div class="bm-value">{len(area_stats_global)}</div>
                    <div style="font-size:0.8rem; color:#64748B;">Participando en la contratación.</div></div>''', unsafe_allow_html=True)

# ================================================================
# 05. EXPLORADOR (Colapsado para limpiar la vista principal)
# ================================================================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🔎 Explorador de Datos Detallado y Extracciones"):
    st.dataframe(
        df[['Annio_PAA','CONTRATO_Referencia','CONTRATO_Objeto',
            'Valor_Esperado_PAA','CONTRATO_Valor_Inicial','CONTRATO_Valor',
            'KPI_Dias_Desfase','KPI_Desviacion_Valor',
            'CONTRATO_Nombre_Contratista','CONTRATO_Estado']],
        use_container_width=True
    )
    
    st.download_button(label="📥 Exportar CSV", data=df.to_csv(index=False, encoding='utf-8-sig'),
                       file_name="icc_abastecimiento_filtrado.csv", mime="text/csv")
