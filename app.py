import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ================================================================
# CONFIGURACIÓN
# ================================================================
st.set_page_config(
    page_title="Radar ICFES — Dashboard Integral de Contratación",
    
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #F8FAFC; }
    .main .block-container { padding-top: 1rem; max-width: 1500px; }
    
    /* CABECERA (Header) */
    .dashboard-header {
        background: #FFFFFF;
        color: #004884;
        padding: 1.8rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border-top: 5px solid #004884;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .dashboard-header h1 { margin: 0; font-weight: 800; font-size: 1.8rem; letter-spacing: -0.5px; }
    .dashboard-header p { margin: 0.5rem 0 0 0; color: #64748B; font-size: 0.9rem; font-weight: 400; }
    .header-badge {
        display: inline-block; background: #EEF2FF; color: #004884; padding: 0.3rem 0.8rem;
        border-radius: 20px; font-size: 0.75rem; font-weight: 600; margin-top: 0.8rem;
    }
    
    /* ENCABEZADOS DE SECCIÓN */
    .section-header {
        display: flex; align-items: center; gap: 12px;
        margin: 2rem 0 1rem 0; padding-bottom: 0.6rem; border-bottom: 1px solid #E2E8F0;
    }
    .section-header .section-number {
        background: #004884; color: white;
        width: 28px; height: 28px; border-radius: 6px;
        display: flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.8rem; flex-shrink: 0;
    }
    .section-header h2 { margin: 0; font-weight: 700; font-size: 1.25rem; color: #0F172A; letter-spacing: -0.3px; }
    
    /* TARJETAS KPI */
    .kpi-card {
        background: #FFFFFF; border: none; border-radius: 12px;
        padding: 1.2rem 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); transform: translateY(-2px); }
    .kpi-label { font-size: 0.75rem; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 0.4rem; }
    .kpi-value { font-size: 1.8rem; font-weight: 800; color: #004884; line-height: 1.1; letter-spacing: -0.5px; }
    .kpi-delta { font-size: 0.75rem; font-weight: 500; margin-top: 0.4rem; display: flex; align-items: center; gap: 4px; }
    .kpi-delta.positive { color: #009639; }
    .kpi-delta.negative { color: #E03C31; }
    .kpi-delta.neutral { color: #64748B; }

    /* ETIQUETAS Y TEXTOS */
    .area-tag {
        display: inline-block; background: #F1F5F9;
        border: none; padding: 0.2rem 0.7rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; color: #004884; margin: 0.1rem;
    }
    .clean-subheader { font-size: 0.95rem; font-weight: 600; color: #334155; margin: 0.3rem 0; }
    .question-label { font-size: 0.85rem; font-weight: 600; color: #64748B; font-style: normal; margin-bottom: 0.5rem; }
    
    /* TARJETA BENCHMARK */
    .benchmark-card {
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 10px;
        padding: 1rem 1.2rem; margin-bottom: 0.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .benchmark-card .bm-label { font-size: 0.7rem; font-weight: 600; color: #004884; text-transform: uppercase; letter-spacing: 0.5px; }
    .benchmark-card .bm-value { font-size: 1.1rem; font-weight: 700; color: #0F172A; margin: 0.2rem 0; }
    .benchmark-card .bm-rank { font-size: 0.7rem; color: #64748B; }
    
    /* SIDEBAR Y FOOTER */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    .sidebar-title { font-size: 0.8rem; font-weight: 700; color: #004884; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.8rem; padding-bottom: 0.4rem; border-bottom: 2px solid #E2E8F0; }
    .dashboard-footer { text-align: center; padding: 1.5rem 0; color: #94A3B8; font-size: 0.75rem; border-top: 1px solid #F1F5F9; margin-top: 2rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .tab-metric { font-size: 0.85rem; color: #475569; padding: 0.3rem 0; }
</style>
""", unsafe_allow_html=True)

# PALETA CORPORATIVA ICFES
COLORS = {
    'azul': '#004884',        # Azul ICFES
    'oro': '#FFD100',         # Amarillo ICFES
    'verde': '#009639',       # Verde Aprobación/Meta
    'rojo': '#E03C31',        # Rojo Alerta
    'azul_claro': '#007ECC',  # Cian de apoyo
    'indigo': '#1E3A8A',      # Azul Marino
    'gris': '#64748B', 
    'slate': '#334155',
    'palette': ['#004884', '#FFD100', '#009639', '#E03C31', '#007ECC',
                '#64748B', '#1E3A8A', '#F59E0B', '#10B981', '#6366F1',
                '#8B5CF6', '#EC4899']
}
PLOTLY_TEMPLATE = 'plotly_white'

# ── Utilidades ──
def fmt_cop(valor):
    if pd.isna(valor) or valor == 0: return "$0"
    if abs(valor) >= 1e12: return f"${valor/1e12:,.2f} B"
    if abs(valor) >= 1e9: return f"${valor/1e9:,.1f} MM"
    elif abs(valor) >= 1e6: return f"${valor/1e6:,.1f} M"
    else: return f"${valor:,.0f}"

# FIX 3: Formatter para ejes Plotly (no usar G/B anglosajón)
def fmt_plotly_cop(valor):
    """Formatea valores monetarios para ejes de Plotly (retorna string corto)."""
    if abs(valor) >= 1e12: return f"${valor/1e12:.1f}B"
    if abs(valor) >= 1e9: return f"${valor/1e9:.0f}MM"
    if abs(valor) >= 1e6: return f"${valor/1e6:.0f}M"
    return f"${valor:,.0f}"

# FIX 5: Abreviar nombres de áreas para gráficos
def abreviar_area(nombre, max_len=40):
    """Abrevia nombres de áreas ICFES para ejes de gráficos."""
    abreviaturas = {
        'Subdirección': 'Subdir.',
        'Dirección': 'Dir.',
        'Oficina Asesora': 'Of. Asesora',
        'Oficina de': 'Of.',
        'Tecnología e Información': 'TI',
        'y Servicios Generales': 'y Serv. Grales.',
        'Aplicación de Instrumentos': 'Aplic. Instrumentos',
        'Diseño de Instrumentos': 'Diseño Instrum.',
        'Análisis y Divulgación': 'Análisis y Divulg.',
        'Producción y Operaciones': 'Prod. y Oper.',
        'Gestión de Proyectos de Investigación': 'Gest. Proy. Inv.',
        'Talento Humano': 'Talento Hum.',
    }
    resultado = str(nombre)
    for largo, corto in abreviaturas.items():
        resultado = resultado.replace(largo, corto)
    if len(resultado) > max_len:
        resultado = resultado[:max_len-2] + '..'
    return resultado

def section_header(number, title):
    st.markdown(f'<div class="section-header"><div class="section-number">{number}</div><h2>{title}</h2></div>', unsafe_allow_html=True)

def kpi_card(label, value, delta=None, delta_type="neutral"):
    delta_html = f'<div class="kpi-delta {delta_type}">{delta}</div>' if delta else ""
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div>{delta_html}</div>', unsafe_allow_html=True)

def benchmark_card(label, value, rank_text=""):
    rank_html = f'<div class="bm-rank">{rank_text}</div>' if rank_text else ""
    st.markdown(f'<div class="benchmark-card"><div class="bm-label">{label}</div><div class="bm-value">{value}</div>{rank_html}</div>', unsafe_allow_html=True)

def question(text):
    st.markdown(f'<p class="question-label">{text}</p>', unsafe_allow_html=True)

# ================================================================
# DATOS
# ================================================================
@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), 'Base_Cruzada_Maestra_24_25.xlsx')
    df = pd.read_excel(ruta, sheet_name='Maestra_24_25', engine='openpyxl')
    
    cols_numericas = [
        'CONTRATO_Valor', 'CONTRATO_Valor_Inicial', 'Valor_Esperado_PAA',
        'KPI_Dias_Desfase', 'KPI_Desviacion_Valor', 'KPI_Desviacion_Pct',
        'KPI_Crecimiento_Contractual', 'KPI_Concentracion_Contratista', 'KPI_Desfase_Duracion'
    ]
    cols_texto = [
        'CONTRATO_Area', 'CONTRATO_Estado', 'CONTRATO_Referencia', 'CONTRATO_Objeto',
        'CONTRATO_Nombre_Contratista', 'CONTRATO_Naturaleza_Juridica', 'CONTRATO_Genero'
    ]
    
    # FIX 2: Desfase = NaN (no 0) cuando no hay dato real
    for col in cols_numericas:
        if col not in df.columns:
            df[col] = 0 if col != 'KPI_Dias_Desfase' else np.nan
        if col == 'KPI_Dias_Desfase':
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Mantener NaN
            # Solo marcar como NaN los desfases de registros sin contrato real
            mask_sin_contrato = df.get('CONTRATO_Valor', pd.Series(dtype=float)).fillna(0) == 0
            df.loc[mask_sin_contrato, col] = np.nan
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    for col in cols_texto:
        if col not in df.columns:
            df[col] = 'No Registra'
        df[col] = df[col].fillna('No Registra').astype(str).str.strip()

    if 'Annio_PAA' not in df.columns:
        df['Annio_PAA'] = 0
    df['Annio_PAA'] = pd.to_numeric(df['Annio_PAA'], errors='coerce').fillna(0).astype('Int64')
    
    if 'CONTRATO_Fecha_Firma' in df.columns:
        df['CONTRATO_Fecha_Firma'] = pd.to_datetime(df['CONTRATO_Fecha_Firma'], errors='coerce')
    else:
        df['CONTRATO_Fecha_Firma'] = pd.NaT
    
    df['CONTRATO_Estado'] = df['CONTRATO_Estado'].str.capitalize()

    # Limpiar nombres de área (quitar saltos de línea)
    df['CONTRATO_Area'] = df['CONTRATO_Area'].str.replace(r'\n', ' ', regex=True).str.strip()
    
    # FIX HOMOLOGACIÓN: Alinear áreas sucias de SECOP con el catálogo oficial del ICFES
    map_oficial = {
        'Dirección de Tecnología e Información Dirección de Producción y Operaciones': 'Dirección de Tecnología e Información',
        'Dirección de Tecnología e Información Oficina Asesora de Comunicaciones y Mercadeo Oficina Asesora de Planeación': 'Dirección de Tecnología e Información',
        'Oficina Asesora de Comunicaciones y Mercadeo Oficina Asesora de Planeación': 'Oficina Asesora de Comunicaciones y Mercadeo',
        'Oficina de Gestión de Proyectos de Investigación': 'Oficina Asesora de Gestión de Proyectos de Investigación',
        'Secretaría Genera Subdirección de Información': 'Subdirección de Información',
        'Secretaría General - Unidad de Atencion al Ciudadano': 'Unidad de Atención al Ciudadano',
        'Subdirección de Aplicación de Instrumentos Dirección de Tecnología e Información': 'Subdirección de Aplicación de Instrumentos',
        'Subdirección de Información Oficina Asesora de Planeación': 'Subdirección de Información',
        'Subdirección de Información Secretaría General': 'Subdirección de Información'
    }
    df['CONTRATO_Area'] = df['CONTRATO_Area'].replace(map_oficial)
    
    # FIX 1: Filtrar contratos fantasma ($0 en ambos valores + sin area)
    mask_fantasma = (
        (df['CONTRATO_Valor'] == 0) & 
        (df['CONTRATO_Valor_Inicial'] == 0) & 
        (df['CONTRATO_Area'] == 'No Registra')
    )
    df = df[~mask_fantasma].copy()

    return df

df_all = cargar_datos()

# ================================================================
# SIDEBAR — FILTROS
# ================================================================
logo_path = os.path.join(os.path.dirname(__file__), 'icfes_logo.png')
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, width=150)

st.sidebar.markdown('<div class="sidebar-title">Filtros de Análisis</div>', unsafe_allow_html=True)

# Filtro de Año
years = sorted([y for y in df_all['Annio_PAA'].unique() if y != 0 and pd.notna(y)])
sel_years = st.sidebar.multiselect("Vigencia", years, default=years)

# Filtro de Área — clave del rediseño
# FIX 4: Excluir 'No Registra' del catálogo de áreas
areas_disponibles = sorted([a for a in df_all['CONTRATO_Area'].unique() if a != 'No Registra'])
TODAS = "Todas las Áreas"
opcion_area = st.sidebar.selectbox(
    "Área del ICFES",
    [TODAS] + areas_disponibles,
    index=0
)

vista_global = (opcion_area == TODAS)
if vista_global:
    sel_areas = areas_disponibles
else:
    sel_areas = [opcion_area]

# Filtro de Estado
estados = sorted(df_all['CONTRATO_Estado'].unique())
sel_estados = st.sidebar.multiselect("Estado", estados, default=estados)

# Aplicar filtros
df = df_all[
    (df_all['Annio_PAA'].isin(sel_years)) &
    (df_all['CONTRATO_Area'].isin(sel_areas)) &
    (df_all['CONTRATO_Estado'].isin(sel_estados))
].copy()

# Estadísticas del sidebar
st.sidebar.markdown("---")
n_areas_sel = df['CONTRATO_Area'].nunique()
st.sidebar.markdown(f"**{len(df):,}** registros seleccionados")
st.sidebar.markdown(f"**{n_areas_sel}** áreas · **{df['CONTRATO_Nombre_Contratista'].nunique()}** contratistas")
st.sidebar.markdown(f"*De {len(df_all):,} contratos totales ICFES*")

# ================================================================
# ENCABEZADO
# ================================================================
area_display = "Todas las Áreas" if vista_global else opcion_area
years_display = ", ".join(str(y) for y in sel_years) if sel_years else "Sin vigencia"

st.markdown(f"""
<div class="dashboard-header">
    <h1>Radar ICFES — Contratación Integral</h1>
    <p>Dashboard de gestión contractual  ·  Base Cruzada Maestra Auditada  ·  {years_display}</p>
    <div class="header-badge">{area_display} · {len(df):,} contratos</div>
</div>
""", unsafe_allow_html=True)

# ── Guardia de datos vacíos ──
if len(df) == 0:
    st.warning("**No hay registros** con los filtros seleccionados. Ajusta los filtros en la barra lateral.")
    st.stop()

# ================================================================
# ESTRUCTURA DE TABS (Limitar número de vistas simultáneas)
# ================================================================
tab_exec, tab_fin, tab_time, tab_contr, tab_meta = st.tabs([
    "Resumen Ejecutivo", 
    "Cumplimiento Financiero", 
    "Tiempos de Etapas", 
    "Perfil y Contratistas",
    "Metodología"
])

# ================================================================
with tab_exec:
    # 01. KPIs EJECUTIVOS
    # ================================================================
    titulo_kpi = "Resumen Ejecutivo — " + (area_display if not vista_global else "ICFES Consolidado")
    section_header("01", titulo_kpi)

    total = len(df)
    valor_total = df['CONTRATO_Valor'].sum()
    paa_total = df['Valor_Esperado_PAA'].sum()
    desv_neta = df['KPI_Desviacion_Valor'].sum()
    desfase_prom = df['KPI_Dias_Desfase'].mean()
    desfase_med = df['KPI_Dias_Desfase'].median()
    contratistas_unicos = df['CONTRATO_Nombre_Contratista'].nunique()

    # Comparación interanual
    if len(sel_years) >= 2:
        y_curr = max(sel_years)
        y_prev = sorted(sel_years)[-2]
        d_prev = df[df['Annio_PAA'] == y_prev]
        d_curr = df[df['Annio_PAA'] == y_curr]
        dc = len(d_curr) - len(d_prev)
        dv = d_curr['CONTRATO_Valor'].sum() - d_prev['CONTRATO_Valor'].sum()
        dt_c = d_curr['KPI_Dias_Desfase'].mean()
        dt_p = d_prev['KPI_Dias_Desfase'].mean()
        dt = dt_c - dt_p if not pd.isna(dt_c) and not pd.isna(dt_p) else None
    else:
        dc = dv = dt = None

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Total Contratos", f"{total:,}",
                 f"{'▲' if dc and dc>0 else '▼'} {abs(dc):,} vs año ant." if dc is not None else None,
                 "negative" if dc and dc<0 else "positive")
    with c2:
        kpi_card("Valor Contratado", fmt_cop(valor_total),
                 f"{'▲' if dv and dv>0 else '▼'} {fmt_cop(abs(dv))}" if dv is not None else None,
                 "positive" if dv and dv>0 else "negative")
    with c3:
        kpi_card("Presupuesto PAA", fmt_cop(paa_total))
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    c4, c5, c6 = st.columns(3)
    with c4:
        if desv_neta == 0:
            kpi_card("Balance Neto", "Equilibrado")
        else:
            estado_d = "Ahorro" if desv_neta < 0 else "Sobrecosto"
            tipo_d = "positive" if desv_neta < 0 else "negative"
            kpi_card("Balance Neto", fmt_cop(abs(desv_neta)), estado_d, tipo_d)
    with c5:
        kpi_card("Desfase Prom / Med", f"{desfase_prom:.0f} / {desfase_med:.0f} d" if not pd.isna(desfase_prom) else "N/A",
                 f"{'▲' if dt and dt>0 else '▼'} {abs(dt):.0f} d" if dt is not None else None,
                 "positive" if dt and dt<0 else "negative")
    with c6:
        pct_ejec = (valor_total / paa_total * 100) if paa_total > 0 else 0
        kpi_card("% Ejecución", f"{pct_ejec:.1f}%",
                 f"{contratistas_unicos:,} contratistas únicos", "neutral")

    st.markdown("<br>", unsafe_allow_html=True)

    # ================================================================
    # 02. PANORAMA INTER-ÁREAS (solo en vista global)
    # ================================================================
    if vista_global:
        section_header("02", "Panorama Comparativo — Todas las Áreas del ICFES")
    
        area_stats = df.groupby('CONTRATO_Area').agg(
            Contratos=('CONTRATO_Referencia', 'count'),
            Valor_Total=('CONTRATO_Valor', 'sum'),
            Valor_Promedio=('CONTRATO_Valor', 'mean'),
            PAA_Total=('Valor_Esperado_PAA', 'sum'),
            Desviacion_Neta=('KPI_Desviacion_Valor', 'sum'),
            Desfase_Promedio=('KPI_Dias_Desfase', 'mean'),
            Contratistas=('CONTRATO_Nombre_Contratista', 'nunique')
        ).reset_index()
    
        area_stats['Ejecucion_Pct'] = np.where(
            area_stats['PAA_Total'] > 0,
            (area_stats['Valor_Total'] / area_stats['PAA_Total'] * 100).round(1),
            0
        )
        area_stats['Nombre_Corto'] = area_stats['CONTRATO_Area'].apply(abreviar_area)
        area_stats = area_stats.sort_values('Valor_Total', ascending=False)
    
        col_a, col_b = st.columns(2)
    
        with col_a:
            question("¿Cuánto pesa cada área en el presupuesto total del ICFES?")
            top_val = area_stats.head(12).copy()
            top_val['Texto_Valor'] = top_val['Valor_Total'].apply(fmt_plotly_cop)
            fig = px.bar(top_val, y='Nombre_Corto', x='Valor_Total', orientation='h',
                         text='Texto_Valor', template=PLOTLY_TEMPLATE,
                         color_discrete_sequence=[COLORS['azul']],
                         labels={'Nombre_Corto':'', 'Valor_Total':'Valor Total ($COP)'})
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=450)
            fig.update_traces(textposition='outside', hovertemplate='<b>Área:</b> %{y}<br><b>Valor Total:</b> %{text}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)
    
        with col_b:
            question("¿Qué áreas presentan mayor desfase promedio en días?")
            desfase_data = area_stats[area_stats['Desfase_Promedio'].notna() & (area_stats['CONTRATO_Area'] != 'No Registra')].sort_values('Desfase_Promedio', ascending=True).head(12)
            colors_d = [COLORS['rojo'] if v > 30 else COLORS['oro'] if v > 10 else COLORS['verde'] for v in desfase_data['Desfase_Promedio']]
            fig = px.bar(desfase_data, y='Nombre_Corto', x='Desfase_Promedio', orientation='h',
                         text_auto='.1f', template=PLOTLY_TEMPLATE,
                         labels={'Nombre_Corto':'', 'Desfase_Promedio':'Desfase Promedio (días)'})
            fig.update_traces(marker_color=colors_d, textposition='outside', hovertemplate='<b>Área:</b> %{y}<br><b>Desfase:</b> %{x} días<extra></extra>')
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=450)
            st.plotly_chart(fig, use_container_width=True)
    
        # Tabla resumen de áreas
        question("Resumen estadístico por área — haz clic en las columnas para ordenar")
        area_display_df = area_stats[['Nombre_Corto','Contratos','Valor_Total','PAA_Total','Ejecucion_Pct','Desfase_Promedio','Contratistas']].copy()
        area_display_df.columns = ['Área', 'Contratos', 'Valor Contratado', 'Presupuesto PAA', '% Ejecución', 'Desfase Prom (d)', 'Contratistas']
        area_display_df['Valor Contratado'] = area_display_df['Valor Contratado'].apply(fmt_cop)
        area_display_df['Presupuesto PAA'] = area_display_df['Presupuesto PAA'].apply(fmt_cop)
        area_display_df['Desfase Prom (d)'] = area_display_df['Desfase Prom (d)'].round(1)
        st.dataframe(area_display_df, use_container_width=True, hide_index=True, height=400)

        st.markdown("<br>", unsafe_allow_html=True)


# ================================================================
with tab_fin:
    # 03. EJECUCIÓN PRESUPUESTAL
    # ================================================================
    section_header("03" if vista_global else "02", "Ejecución Presupuestal")

    col1, col2 = st.columns(2)

    with col1:
        question("¿Cuánto se planeó gastar (PAA) vs cuánto se contrató realmente?")
        fin = df.groupby('Annio_PAA').agg(
            Valor_Real=('CONTRATO_Valor', 'sum'),
            PAA=('Valor_Esperado_PAA', 'sum')
        ).reset_index()
    
        fm = fin[['Annio_PAA', 'PAA', 'Valor_Real']].melt(id_vars='Annio_PAA', var_name='Tipo', value_name='Valor')
        fm['Tipo'] = fm['Tipo'].map({'PAA': 'Planeado (PAA)', 'Valor_Real': 'Contratado Real'})
        fm['Texto_Valor'] = fm['Valor'].apply(fmt_plotly_cop)
        fig = px.bar(fm, x='Annio_PAA', y='Valor', color='Tipo', barmode='group', text='Texto_Valor',
                     color_discrete_map={'Planeado (PAA)': COLORS['azul'], 'Contratado Real': COLORS['oro']},
                     labels={'Valor':'Pesos ($COP)', 'Annio_PAA':'Año'}, template=PLOTLY_TEMPLATE)
        fig.update_layout(xaxis_tickvals=years, legend=dict(orientation='h', y=-0.15), height=400)
        fig.update_yaxes(tickprefix='$', tickformat=',.0f')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        question("¿Qué contratos generaron la mayor desviación presupuestal?")
        top_desv = df[df['KPI_Desviacion_Valor'] != 0].nlargest(10, 'KPI_Desviacion_Valor')[
            ['CONTRATO_Referencia', 'KPI_Desviacion_Valor', 'CONTRATO_Nombre_Contratista', 'CONTRATO_Area']]
        if len(top_desv) > 0:
            top_desv['Nombre_Corto'] = top_desv['CONTRATO_Referencia']
            top_desv['Texto_Valor'] = top_desv['KPI_Desviacion_Valor'].apply(fmt_plotly_cop)
            fig = px.bar(top_desv, y='Nombre_Corto', x='KPI_Desviacion_Valor', orientation='h',
                         text='Texto_Valor', template=PLOTLY_TEMPLATE,
                         color_discrete_sequence=[COLORS['azul']],
                         labels={'KPI_Desviacion_Valor':'Desviación ($COP)', 'Nombre_Corto':''})
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, clickmode='event+select')
            fig.update_traces(textposition='outside', hovertemplate='<b>Área:</b> %{y}<br><b>Valor Total:</b> %{text}<extra></extra>')
            evt = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")
            if evt and len(evt.selection["points"]) > 0:
                sel_ref = evt.selection["points"][0]["y"]
                info = df[df['CONTRATO_Referencia'] == sel_ref]
                if not info.empty:
                    i = info.iloc[0]
                    st.info(f"**{i['CONTRATO_Referencia']}** · {i['CONTRATO_Area'][:40]}  \n"
                            f"**Contratista:** {i['CONTRATO_Nombre_Contratista']}  \n"
                            f"**Objeto:** {str(i['CONTRATO_Objeto'])[:200]}")
        else:
            st.info("No hay desviaciones presupuestales en los datos seleccionados.")


# ================================================================
with tab_time:
    # 04. OPORTUNIDAD EN LA CONTRATACIÓN
    # ================================================================
    section_header("04" if vista_global else "03", "Oportunidad en la Contratación")

    col3, col4 = st.columns(2)

    with col3:
        question("¿Cuántos contratos se firmaron a tiempo vs con retraso?")
        timing = df[df['KPI_Dias_Desfase'].notna()].copy()
        if len(timing) > 0:
            timing['Puntualidad'] = np.where(timing['KPI_Dias_Desfase'] <= 0, 'A tiempo', 'Con retraso')
            tc = timing.groupby(['Annio_PAA', 'Puntualidad']).size().reset_index(name='Contratos')
            fig = px.bar(tc, x='Annio_PAA', y='Contratos', color='Puntualidad', barmode='group', text_auto=True,
                         color_discrete_map={'A tiempo': COLORS['verde'], 'Con retraso': COLORS['rojo']},
                         labels={'Annio_PAA': 'Año'}, template=PLOTLY_TEMPLATE)
            fig.update_layout(xaxis_tickvals=years, legend=dict(orientation='h', y=-0.15), height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de desfase disponibles.")

    with col4:
        question("¿En qué meses se concentran las firmas de contratos?")
        df_mes = df[df['CONTRATO_Fecha_Firma'].notna()].copy()
        if len(df_mes) > 0:
            df_mes['Mes'] = df_mes['CONTRATO_Fecha_Firma'].dt.month
            mc = df_mes.groupby(['Annio_PAA', 'Mes']).size().reset_index(name='Contratos')
            ml = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
            mc['Mes_Nombre'] = mc['Mes'].map(ml)
            fig = px.line(mc, x='Mes_Nombre', y='Contratos', color='Annio_PAA', markers=True,
                          labels={'Annio_PAA':'Año', 'Mes_Nombre':'Mes'}, template=PLOTLY_TEMPLATE,
                          color_discrete_sequence=[COLORS['azul'], COLORS['oro']])
            fig.update_layout(xaxis={'categoryorder':'array', 'categoryarray':list(ml.values())},
                              legend=dict(orientation='h', y=-0.15), height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de fecha de firma disponibles.")


# ================================================================
with tab_contr:
    # 05. PRINCIPALES CONTRATISTAS
    # ================================================================
    section_header("05" if vista_global else "04", "Principales Contratistas")

    question("¿Quiénes son los contratistas con mayor volumen?")
    tv = df.groupby('CONTRATO_Nombre_Contratista').agg(
        Valor_Total=('CONTRATO_Valor', 'sum'),
        Num_Contratos=('CONTRATO_Referencia', 'count'),
        Areas=('CONTRATO_Area', 'nunique')
    ).reset_index().nlargest(15, 'Valor_Total')

    tv['Nombre'] = tv['CONTRATO_Nombre_Contratista'].str[:50]
    tv['Texto'] = tv.apply(lambda r: f"{fmt_cop(r['Valor_Total'])} ({r['Num_Contratos']} cto{'s' if r['Num_Contratos']>1 else ''}, {r['Areas']} área{'s' if r['Areas']>1 else ''})", axis=1)

    fig = px.bar(tv, y='Nombre', x='Valor_Total', orientation='h', text='Texto',
                 color_discrete_sequence=[COLORS['azul']], template=PLOTLY_TEMPLATE,
                 labels={'Nombre':'', 'Valor_Total':'Valor Total ($COP)'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=500, clickmode='event+select')
    fig.update_traces(textposition='outside', hovertemplate='<b>Área:</b> %{y}<br><b>Valor Total:</b> %{text}<extra></extra>')
    evt2 = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

    if evt2 and len(evt2.selection["points"]) > 0:
        sel_nombre = evt2.selection["points"][0]["y"]
        matches = df[df['CONTRATO_Nombre_Contratista'].str.startswith(sel_nombre, na=False)]['CONTRATO_Nombre_Contratista'].unique()
        if len(matches) > 0:
            df_cont = df[df['CONTRATO_Nombre_Contratista'] == matches[0]]
            st.markdown(f"**Contratos de: {matches[0]}**")
            st.dataframe(
                df_cont[['Annio_PAA','CONTRATO_Referencia','CONTRATO_Area','CONTRATO_Objeto','CONTRATO_Valor','CONTRATO_Estado']].sort_values('CONTRATO_Valor', ascending=False),
                use_container_width=True, hide_index=True
            )

    # ================================================================
    # 06. PERFIL DEL CONTRATISTA
    # ================================================================
    section_header("06" if vista_global else "05", "Perfil del Contratista")

    col5, col6 = st.columns(2)

    with col5:
        question("¿A quién se contrata: personas naturales o jurídicas?")
        nat = df['CONTRATO_Naturaleza_Juridica'].value_counts().reset_index()
        nat.columns = ['Tipo', 'Contratos']
        nat = nat[nat['Tipo'] != 'No Registra']
        if len(nat) > 0:
            fig = px.pie(nat, names='Tipo', values='Contratos', hole=0.45, hover_data={'Contratos':':.0f'},
                         color_discrete_sequence=[COLORS['azul'], COLORS['oro'], COLORS['azul_claro'], COLORS['gris']],
                         template=PLOTLY_TEMPLATE)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de naturaleza jurídica.")

    with col6:
        question("¿Cuál es la distribución por género en los contratos?")
        gen = df['CONTRATO_Genero'].value_counts().reset_index()
        gen.columns = ['Género', 'Contratos']
        gen = gen[gen['Género'] != 'No Registra']
        if len(gen) > 0:
            fig = px.pie(gen, names='Género', values='Contratos', hole=0.45,
                         color_discrete_sequence=[COLORS['azul'], COLORS['oro'], COLORS['gris']],
                         template=PLOTLY_TEMPLATE)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de género.")


# ================================================================
with tab_fin:
    # 07. ADICIONES Y MODIFICACIONES
    # ================================================================
    section_header("07" if vista_global else "06", "Adiciones y Modificaciones Contractuales")

    col7, col8 = st.columns(2)
    kv = df[df['KPI_Crecimiento_Contractual'].notna() & (df['KPI_Crecimiento_Contractual'] != 0)]

    with col7:
        question("¿Cuántos contratos crecieron con adiciones?")
        if len(kv) > 0:
            cr = kv.groupby('Annio_PAA').apply(
                lambda g: pd.Series({
                    'Con adiciones': int((g['KPI_Crecimiento_Contractual'] > 1).sum()),
                    'Sin crecimiento': int((g['KPI_Crecimiento_Contractual'] <= 1).sum())
                })
            ).reset_index()
            cm = cr.melt(id_vars='Annio_PAA', var_name='Resultado', value_name='Contratos')
            fig = px.bar(cm, x='Annio_PAA', y='Contratos', color='Resultado', barmode='group', text_auto=True,
                         color_discrete_map={'Con adiciones': COLORS['rojo'], 'Sin crecimiento': COLORS['verde']},
                         labels={'Annio_PAA':'Año'}, template=PLOTLY_TEMPLATE)
            fig.update_layout(xaxis_tickvals=years, legend=dict(orientation='h', y=-0.15), height=380)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de crecimiento contractual.")

    with col8:
        question("¿Cuáles contratos crecieron más?")
        if len(kv) > 0:
            kv_crecidos = kv[kv['KPI_Crecimiento_Contractual'] > 1].copy()
            if len(kv_crecidos) > 0:
                tc = kv_crecidos.nlargest(10, 'KPI_Crecimiento_Contractual')[
                    ['CONTRATO_Referencia', 'KPI_Crecimiento_Contractual', 'CONTRATO_Valor_Inicial', 'CONTRATO_Valor', 'CONTRATO_Area']].copy()
                # FIX 6: Mostrar monto absoluto de adición + ratio
                tc['Adicion_Abs'] = tc['CONTRATO_Valor'] - tc['CONTRATO_Valor_Inicial']
                tc['Texto'] = tc.apply(lambda r: f"{r['KPI_Crecimiento_Contractual']:.2f}x (+{fmt_cop(r['Adicion_Abs'])})", axis=1)
                fig = px.bar(tc, y='CONTRATO_Referencia', x='KPI_Crecimiento_Contractual', orientation='h',
                             text='Texto', template=PLOTLY_TEMPLATE,
                             color_discrete_sequence=[COLORS['rojo']],
                             labels={'KPI_Crecimiento_Contractual':'Veces que creció', 'CONTRATO_Referencia':''})
                fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=420, margin=dict(r=180))
                fig.update_traces(texttemplate='%{text}', textposition='outside', textfont_size=11, cliponaxis=False, hovertemplate='<b>Contrato:</b> %{y}<br><b>Aumento de:</b> %{text}<extra></extra>')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay contratos con adiciones en la selección actual.")
        else:
            st.info("No hay datos de crecimiento contractual.")


# ================================================================
with tab_contr:
    # 08. EXPLORADOR DE DATOS GRANULAR
    # ================================================================
    section_header("08" if vista_global else "07", "Explorador de Datos — Nivel Granular")

    # Subfiltros para exploración
    st.markdown("**Filtros adicionales para exploración de detalle:**")
    exp_c1, exp_c2, exp_c3 = st.columns(3)

    with exp_c1:
        buscar_contrato = st.text_input("Buscar contrato (referencia)", placeholder="Ej: ICFES-242")
    with exp_c2:
        buscar_contratista = st.text_input("Buscar contratista", placeholder="Ej: Infotic")
    with exp_c3:
        rango_valor = st.selectbox("Rango de valor", [
            "Todos", "Menor a $50M", "$50M - $500M", "$500M - $1,000M", "Mayor a $1,000M"
        ])

    df_explorador = df.copy()

    if buscar_contrato:
        df_explorador = df_explorador[df_explorador['CONTRATO_Referencia'].str.contains(buscar_contrato, case=False, na=False)]
    if buscar_contratista:
        df_explorador = df_explorador[df_explorador['CONTRATO_Nombre_Contratista'].str.contains(buscar_contratista, case=False, na=False)]
    if rango_valor == "Menor a $50M":
        df_explorador = df_explorador[df_explorador['CONTRATO_Valor'] < 50_000_000]
    elif rango_valor == "$50M - $500M":
        df_explorador = df_explorador[(df_explorador['CONTRATO_Valor'] >= 50_000_000) & (df_explorador['CONTRATO_Valor'] < 500_000_000)]
    elif rango_valor == "$500M - $1,000M":
        df_explorador = df_explorador[(df_explorador['CONTRATO_Valor'] >= 500_000_000) & (df_explorador['CONTRATO_Valor'] < 1_000_000_000)]
    elif rango_valor == "Mayor a $1,000M":
        df_explorador = df_explorador[df_explorador['CONTRATO_Valor'] >= 1_000_000_000]

    st.markdown(f"**{len(df_explorador):,}** contratos encontrados")

    cols_display = ['Annio_PAA', 'CONTRATO_Referencia', 'CONTRATO_Area', 'CONTRATO_Objeto',
                    'CONTRATO_Valor_Inicial', 'CONTRATO_Valor', 'Valor_Esperado_PAA',
                    'KPI_Desviacion_Valor', 'KPI_Dias_Desfase', 'KPI_Crecimiento_Contractual',
                    'CONTRATO_Nombre_Contratista', 'CONTRATO_Estado']

    cols_available = [c for c in cols_display if c in df_explorador.columns]

    st.dataframe(
        df_explorador[cols_available].sort_values('CONTRATO_Valor', ascending=False),
        use_container_width=True, height=500, hide_index=True
    )

    # Detalle de contrato seleccionado
    st.markdown("---")
    st.markdown("**Detalle de contrato individual:**")
    contratos_lista = df_explorador['CONTRATO_Referencia'].sort_values().unique()
    if len(contratos_lista) > 0:
        sel_contrato = st.selectbox("Seleccionar contrato", contratos_lista, index=0)
        detalle = df_explorador[df_explorador['CONTRATO_Referencia'] == sel_contrato]
        if not detalle.empty:
            d = detalle.iloc[0]
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                st.markdown(f"**Referencia:** {d['CONTRATO_Referencia']}")
                st.markdown(f"**Año:** {d['Annio_PAA']}")
                st.markdown(f"**Área:** {d['CONTRATO_Area']}")
                st.markdown(f"**Estado:** {d['CONTRATO_Estado']}")
            with dc2:
                st.markdown(f"**Valor Inicial:** {fmt_cop(d['CONTRATO_Valor_Inicial'])}")
                st.markdown(f"**Valor Final:** {fmt_cop(d['CONTRATO_Valor'])}")
                st.markdown(f"**PAA Esperado:** {fmt_cop(d['Valor_Esperado_PAA'])}")
                crecimiento = d['KPI_Crecimiento_Contractual']
                st.markdown(f"**Crecimiento:** {crecimiento:.2f}x" if crecimiento > 0 else "**Crecimiento:** N/A")
            with dc3:
                st.markdown(f"**Contratista:** {d['CONTRATO_Nombre_Contratista']}")
                st.markdown(f"**Naturaleza:** {d['CONTRATO_Naturaleza_Juridica']}")
                st.markdown(f"**Desfase:** {d['KPI_Dias_Desfase']:.0f} días" if d['KPI_Dias_Desfase'] != 0 else "**Desfase:** N/A")
                st.markdown(f"**Desviación:** {fmt_cop(d['KPI_Desviacion_Valor'])}")
        
            st.markdown(f"**Objeto:** {d['CONTRATO_Objeto']}")


# ================================================================
with tab_meta:
    # 09. METODOLOGÍA DE CÁLCULO Y DICCIONARIO
    # ================================================================
    st.markdown('''
    <div class="section-header"><div class="section-number">#</div><h2>Metodología y Diccionario de Datos</h2></div>
    ''', unsafe_allow_html=True)
    
    st.markdown('''
    Esta sección documenta la arquitectura de datos y las fórmulas exactas utilizadas para el cálculo de indicadores (KPIs). 
    El rigor analítico evita inferencias asumiendo exclusivamente los cruces estandarizados entre las bases de SECOP II (Contratos) y el Plan Anual de Adquisiciones (PAA).
    ''')
    
    st.markdown("### 1. Fórmulas de Cálculo de Indicadores (KPIs)")
    
    st.markdown("**1.1 Desviación Presupuestal / Balance Neto (`KPI_Desviacion_Valor`)**")
    st.markdown("Mide la eficiencia en la planeación financiera contrastando el valor ejecutado contra lo presupuestado en el PAA.")
    st.latex(r"\text{Desviación} = \text{CONTRATO\_Valor} - \text{Valor\_Esperado\_PAA}")
    st.markdown("- **Si < 0:** Ahorro financiero (Contrato costó menos de lo planeado).")
    st.markdown("- **Si > 0:** Sobrecosto financiero (Contrato excedió la planeación inicial).")
    st.markdown("- **Fuente:** Cruce estricto validado por ID de proceso o justificación PAA.")

    st.markdown("**1.2 Crecimiento Contractual (`KPI_Crecimiento_Contractual`)**")
    st.markdown("Evalúa la ocurrencia de adiciones presupuestales sobre el monto inicial firmado.")
    st.latex(r"\text{Crecimiento} = \left( \frac{\text{CONTRATO\_Valor}}{\text{CONTRATO\_Valor\_Inicial}} \right)")
    st.markdown("- **Si = 1.0:** Ejecución exacta sin adiciones monetarias.")
    st.markdown("- **Si > 1.0:** El contrato sufrió adiciones (ej. 1.25 representa un incremento del 25% sobre la base).")
    
    st.markdown("**1.3 Desfase Contractual (Oportunidad) (`KPI_Dias_Desfase`)**")
    st.markdown("Audita el cumplimiento del calendario propuesto midiendo los días naturales de diferencia entre la estimación y la realidad.")
    st.latex(r"\text{Desfase (días)} = \text{Fecha\_Firma\_Contrato} - \text{Fecha\_Estimada\_PAA}")
    st.markdown("- **Si > 0:** Retraso administrativo (se firmó post-calendario).")
    st.markdown("- **Si ≤ 0:** Contratación oportuna (se firmó antes o durante la fecha límite proyectada).")
    st.markdown("---")

    st.markdown("### 2. Diccionario de Datos Estandarizado")
    
    diccionario_data = [
        {"Variable": "Annio_PAA", "Definición Estricta": "Vigencia fiscal oficial cruzada. Identifica a qué presupuesto temporal pertenece el recurso (2024 o 2025)."},
        {"Variable": "CONTRATO_Area", "Definición Estricta": "Dependencia del ICFES asignada (homologada y purgada de variaciones ortográficas de SECOP)."},
        {"Variable": "CONTRATO_Valor", "Definición Estricta": "El valor monetario TOTAL FINAL del contrato, incluyendo adiciones (si las hubo). Es el número de facturación real."},
        {"Variable": "CONTRATO_Valor_Inicial", "Definición Estricta": "El valor oficial por el cual se sancionó y firmó el contrato en su primer día (sin adiciones)."},
        {"Variable": "Valor_Esperado_PAA", "Definición Estricta": "Tope presupuestal inmovilizado por planeación para llevar a cabo el proceso de la necesidad."},
        {"Variable": "CONTRATO_Referencia", "Definición Estricta": "Identificador alfanumérico único oficial de SECOP que previene la existencia de contratos duplicados o fantasmas en el dashboard."},
        {"Variable": "CONTRATO_Estado", "Definición Estricta": "Status actual del expediente legal en SECOP (Borrador, Celebrado, Liquidado, etc.)."}
    ]
    
    import pandas as pd
    st.dataframe(pd.DataFrame(diccionario_data), use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Descarga
csv = df_explorador.to_csv(index=False, encoding='utf-8-sig')
nombre_archivo = f"datos_icfes_{'global' if vista_global else opcion_area.replace(' ','_')[:30]}.csv"
st.download_button(label="Descargar datos filtrados (CSV)", data=csv,
                   file_name=nombre_archivo, mime="text/csv")

st.markdown('<div class="dashboard-footer">Radar ICFES · Dashboard Integral de Contratación · Base Cruzada Maestra Auditada · 2024–2025</div>', unsafe_allow_html=True)
