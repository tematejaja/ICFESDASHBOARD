import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import os
import unicodedata

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
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-top: 5px solid #004884;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    .dashboard-brand { display: flex; align-items: center; gap: 1.4rem; }
    .dashboard-logo { width: 82px; height: 108px; object-fit: contain; flex-shrink: 0; }
    .dashboard-title { min-width: 0; }
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
        background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
        padding: 1.15rem 1.25rem; box-shadow: 0 3px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        min-height: 148px;
    }
    .kpi-card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.06); transform: translateY(-2px); }
    .kpi-grid {
        display: grid; grid-template-columns: repeat(5, minmax(160px, 1fr));
        gap: 0.75rem; margin: 0.8rem 0 1rem 0;
    }
    .kpi-label { font-size: 0.74rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0; margin-bottom: 0.5rem; }
    .kpi-value { font-size: 1.65rem; font-weight: 800; color: #004884; line-height: 1.15; letter-spacing: 0; overflow-wrap: anywhere; }
    .kpi-context { color: #475569; font-size: 0.76rem; margin-top: 0.55rem; line-height: 1.3; }
    .kpi-delta { font-size: 0.76rem; font-weight: 650; margin-top: 0.35rem; line-height: 1.3; }
    .kpi-delta.positive { color: #009639; }
    .kpi-delta.negative { color: #E03C31; }
    .kpi-delta.neutral { color: #64748B; }
    @media (max-width: 1100px) {
        .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 640px) {
        .main .block-container { padding-left: 0.75rem; padding-right: 0.75rem; }
        .kpi-grid { grid-template-columns: 1fr; }
        .kpi-card { min-height: auto; }
        .dashboard-header { padding: 1.2rem; }
        .dashboard-brand { align-items: flex-start; gap: 0.8rem; }
        .dashboard-logo { width: 58px; height: 78px; }
        .dashboard-header h1 { font-size: 1.35rem; }
    }

    .question-label { font-size: 0.85rem; font-weight: 600; color: #64748B; font-style: normal; margin-bottom: 0.5rem; }
    
    /* SIDEBAR Y FOOTER */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    .sidebar-title { font-size: 0.8rem; font-weight: 700; color: #004884; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.8rem; padding-bottom: 0.4rem; border-bottom: 2px solid #E2E8F0; }
    .dashboard-footer { text-align: center; padding: 1.5rem 0; color: #94A3B8; font-size: 0.75rem; border-top: 1px solid #F1F5F9; margin-top: 2rem; }
    .active-year-badge {
        display: inline-block; background: #E8F2FA; color: #004884;
        border-left: 4px solid #004884; padding: 0.45rem 0.8rem;
        font-size: 0.82rem; font-weight: 650; margin: 0.45rem 0 0.9rem 0;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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
    if pd.isna(valor) or valor == 0:
        return "$0"
    sign = "-" if valor < 0 else ""
    absolute = abs(valor)
    if absolute >= 1e12:
        return f"{sign}${fmt_decimal_es(absolute / 1e12, 2)} billones"
    if absolute >= 1e9:
        return f"{sign}${fmt_decimal_es(absolute / 1e9, 1)} mil millones"
    if absolute >= 1e6:
        return f"{sign}${fmt_decimal_es(absolute / 1e6, 1)} millones"
    return f"{sign}${fmt_decimal_es(absolute, 0)}"

def fmt_plotly_cop(valor):
    if pd.isna(valor):
        return "Sin dato"
    absolute = abs(valor)
    sign = "-" if valor < 0 else ""
    if absolute >= 1e12:
        return f"{sign}${fmt_decimal_es(absolute / 1e12, 1)} billones"
    if absolute >= 1e9:
        return f"{sign}${fmt_decimal_es(absolute / 1e9, 0)} mil millones"
    if absolute >= 1e6:
        return f"{sign}${fmt_decimal_es(absolute / 1e6, 0)} millones"
    return f"{sign}${fmt_decimal_es(absolute, 0)}"

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

def render_kpi_cards(cards):
    items = []
    for card in cards:
        exact_value = card.get("exact_value", card["value"])
        items.append(
            '<div class="kpi-card">'
            f'<div class="kpi-label">{card["label"]}</div>'
            f'<div class="kpi-value" title="{exact_value}">{card["value"]}</div>'
            f'<div class="kpi-context">{card["context"]}</div>'
            f'<div class="kpi-delta {card["delta_type"]}">{card["delta"]}</div>'
            "</div>"
        )
    st.markdown(
        '<div class="kpi-grid">' + "".join(items) + "</div>",
        unsafe_allow_html=True,
    )

def question(text):
    st.markdown(f'<p class="question-label">{text}</p>', unsafe_allow_html=True)


def normalize_state(value):
    text = "No Registra" if pd.isna(value) else str(value).strip()
    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    ).lower()
    normalized = " ".join(normalized.split())
    state_map = {
        "en ejecucion": "En ejecución",
        "terminado": "Terminado",
        "liquidado": "Liquidado",
        "anulado": "Anulado",
        "firmado": "Firmado",
        "suspendido": "Suspendido",
        "no registra": "No Registra",
    }
    return state_map.get(normalized, text.capitalize())


def normalize_legal_nature(value):
    text = "No registra" if pd.isna(value) else str(value).strip()
    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    ).lower()
    normalized = " ".join(normalized.split())
    nature_map = {
        "natural": "Persona natural",
        "persona natural": "Persona natural",
        "juridica": "Persona jurídica",
        "persona juridica": "Persona jurídica",
    }
    return nature_map.get(normalized, "No registra")


def normalize_gender(value):
    text = "No registra" if pd.isna(value) else str(value).strip()
    normalized = unicodedata.normalize("NFD", text)
    normalized = "".join(
        char for char in normalized if unicodedata.category(char) != "Mn"
    ).lower()
    normalized = " ".join(normalized.split())
    gender_map = {
        "femenino": "Femenino",
        "masculino": "Masculino",
    }
    return gender_map.get(normalized, "No registra")


def build_annual_metrics(frame, selected_years):
    rows = []
    for year in sorted(int(value) for value in selected_years):
        annual = frame[frame["Annio_PAA"].eq(year)].copy()
        if annual.empty:
            continue
        timing = annual["KPI_Dias_Desfase"].notna()
        value = annual["CONTRATO_Valor"].sum()
        paa = annual["Valor_Esperado_PAA"].sum()
        balance = value - paa
        rows.append(
            {
                "Annio": year,
                "Contratos": int(annual["CONTRATO_Referencia"].nunique()),
                "Valor": float(value),
                "PAA": float(paa),
                "Ejecucion": float(value / paa * 100) if paa > 0 else np.nan,
                "Balance": float(balance),
                "Balance_Pct": float(balance / paa * 100) if paa > 0 else np.nan,
                "Desfase": float(annual["KPI_Dias_Desfase"].mean()),
                "A_Tiempo": (
                    float(
                        (
                            timing
                            & annual["KPI_Dias_Desfase"].le(0)
                        ).sum()
                        / timing.sum()
                        * 100
                    )
                    if timing.sum()
                    else np.nan
                ),
            }
        )
    return pd.DataFrame(rows)


def performance_status(metric, current, previous):
    if pd.isna(current) or pd.isna(previous):
        return "neutral"
    if metric in {"Ejecucion", "Balance_Pct"}:
        change = abs(previous) - abs(current) if metric == "Balance_Pct" else (
            abs(previous - 100) - abs(current - 100)
        )
        threshold = 0.1
    elif metric == "Desfase":
        change = previous - current
        threshold = 1.0
    else:
        change = current - previous
        threshold = 0.1
    if abs(change) < threshold:
        return "neutral"
    return "positive" if change > 0 else "negative"


def fmt_decimal_es(value, decimals=1):
    if pd.isna(value):
        return "Sin dato"
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_cop_comparison(value):
    return fmt_cop(abs(value))


def comparison_phrase(current, previous, formatter, unit="", threshold=0):
    if pd.isna(current) or pd.isna(previous):
        return "Sin año anterior"
    difference = current - previous
    if abs(difference) < threshold:
        return "Sin cambio frente al año anterior"
    direction = "más" if difference > 0 else "menos"
    formatted = formatter(abs(difference))
    suffix = f" {unit}" if unit else ""
    return f"{formatted}{suffix} {direction} que el año anterior"


def balance_phrase(balance):
    if pd.isna(balance):
        return "Sin PAA calculable"
    if abs(balance) < 0.5:
        return "En línea con el PAA"
    direction = "sobre el PAA" if balance > 0 else "por debajo del PAA"
    return f"{fmt_cop_comparison(balance)} {direction}"


def build_summary_chart(
    metrics, active_year, metric, title, formatter, hover_formatter=None
):
    chart_data = metrics.sort_values("Annio").copy()
    chart_data["Color"] = np.where(
        chart_data["Annio"].eq(active_year),
        COLORS["azul"],
        "#CBD5E1",
    )
    chart_data["Etiqueta"] = chart_data[metric].apply(formatter)
    chart_data["Detalle"] = chart_data[metric].apply(
        hover_formatter or formatter
    )
    fig = go.Figure(
        go.Bar(
            x=chart_data["Annio"].astype(str),
            y=chart_data[metric],
            marker_color=chart_data["Color"],
            text=chart_data["Etiqueta"],
            textposition="outside",
            customdata=np.column_stack(
                [chart_data["Annio"], chart_data["Detalle"]]
            ),
            hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}<extra></extra>",
        )
    )
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text=title, font=dict(size=14, color=COLORS["slate"])),
        height=255,
        margin=dict(l=10, r=10, t=45, b=25),
        showlegend=False,
        xaxis=dict(title="", fixedrange=True),
        yaxis=dict(title="", showticklabels=False, fixedrange=True, rangemode="tozero"),
        hoverlabel=dict(bgcolor="white"),
    )
    return fig

# ================================================================
# DATOS
# ================================================================
REQUIRED_COLUMNS = {
    "Annio_PAA",
    "CONTRATO_Referencia",
    "CONTRATO_Objeto",
    "CONTRATO_Area",
    "CONTRATO_Estado",
    "CONTRATO_Fecha_Firma",
    "CONTRATO_Valor",
    "CONTRATO_Valor_Inicial",
    "Valor_Esperado_PAA",
    "CONTRATO_Nombre_Contratista",
    "CONTRATO_Naturaleza_Juridica",
    "CONTRATO_Genero",
    "KPI_Dias_Desfase",
    "KPI_Desviacion_Valor",
    "KPI_Desviacion_Pct",
    "KPI_Crecimiento_Contractual",
}


@st.cache_data
def cargar_datos():
    ruta = os.path.join(os.path.dirname(__file__), 'Base_Cruzada_Maestra_22_26.xlsx')
    df = pd.read_excel(ruta, sheet_name='Maestra_22_26', engine='openpyxl')

    missing_columns = sorted(REQUIRED_COLUMNS.difference(df.columns))
    if missing_columns:
        raise ValueError(
            "La base no contiene las columnas obligatorias: "
            + ", ".join(missing_columns)
        )

    cols_numericas = [
        'CONTRATO_Valor', 'CONTRATO_Valor_Inicial', 'Valor_Esperado_PAA',
        'KPI_Dias_Desfase', 'KPI_Desviacion_Valor', 'KPI_Desviacion_Pct',
        'KPI_Crecimiento_Contractual'
    ]
    cols_texto = [
        'CONTRATO_Area', 'CONTRATO_Estado', 'CONTRATO_Referencia', 'CONTRATO_Objeto',
        'CONTRATO_Nombre_Contratista', 'CONTRATO_Naturaleza_Juridica', 'CONTRATO_Genero'
    ]

    for col in cols_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    for col in cols_texto:
        df[col] = df[col].fillna('No Registra').astype(str).str.strip()

    df['Annio_PAA'] = pd.to_numeric(df['Annio_PAA'], errors='coerce')
    if df['Annio_PAA'].isna().any():
        raise ValueError("La base contiene vigencias vacías o no numéricas.")
    df['Annio_PAA'] = df['Annio_PAA'].astype(int)
    df['CONTRATO_Fecha_Firma'] = pd.to_datetime(
        df['CONTRATO_Fecha_Firma'], errors='coerce'
    )

    if df['CONTRATO_Referencia'].eq('No Registra').any():
        raise ValueError("La base contiene referencias contractuales vacías.")
    if not df['CONTRATO_Referencia'].is_unique:
        raise ValueError("La base contiene referencias contractuales duplicadas.")

    df['CONTRATO_Estado'] = df['CONTRATO_Estado'].apply(normalize_state)
    df['CONTRATO_Naturaleza_Juridica'] = df[
        'CONTRATO_Naturaleza_Juridica'
    ].apply(normalize_legal_nature)
    df['CONTRATO_Genero'] = df['CONTRATO_Genero'].apply(normalize_gender)

    df['CONTRATO_Area'] = df['CONTRATO_Area'].str.replace(r'\n', ' ', regex=True).str.strip()

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

    mask_fantasma = (
        (df['CONTRATO_Valor'].fillna(0) == 0) &
        (df['CONTRATO_Valor_Inicial'].fillna(0) == 0) &
        (df['CONTRATO_Area'] == 'No Registra')
    )
    df = df[~mask_fantasma].copy()

    return df

try:
    df_all = cargar_datos()
except (FileNotFoundError, ValueError, KeyError) as error:
    st.error(f"No fue posible cargar una base válida: {error}")
    st.stop()

st.sidebar.markdown('<div class="sidebar-title">Filtros de Análisis</div>', unsafe_allow_html=True)

years = sorted([y for y in df_all['Annio_PAA'].unique() if y != 0 and pd.notna(y)])

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

TIPOS_CONTRATISTA = ["Persona natural", "Persona jurídica"]
sel_naturaleza = st.sidebar.multiselect(
    "Tipo de contratista",
    TIPOS_CONTRATISTA,
    default=TIPOS_CONTRATISTA,
)

df_filtrado = df_all[
    (df_all['CONTRATO_Area'].isin(sel_areas)) &
    (df_all['CONTRATO_Estado'].isin(sel_estados)) &
    (df_all['CONTRATO_Naturaleza_Juridica'].isin(sel_naturaleza))
].copy()

st.sidebar.markdown("---")
n_areas_sel = df_filtrado['CONTRATO_Area'].nunique()
st.sidebar.markdown(f"**{len(df_filtrado):,}** registros disponibles")
st.sidebar.markdown(f"**{n_areas_sel}** áreas · **{df_filtrado['CONTRATO_Nombre_Contratista'].nunique()}** contratistas")
st.sidebar.markdown(f"*De {len(df_all):,} contratos totales ICFES*")
naturaleza_no_registrada = int(
    df_all['CONTRATO_Naturaleza_Juridica'].eq('No registra').sum()
)
if naturaleza_no_registrada:
    st.sidebar.caption(
        f"{naturaleza_no_registrada} contratos sin tipo de contratista "
        "no se incluyen en el tablero."
    )

# ================================================================
# ENCABEZADO
# ================================================================
area_display = "Todas las Áreas" if vista_global else opcion_area
years_display = f"{min(years)}–{max(years)}"
logo_path = os.path.join(os.path.dirname(__file__), 'icfes_logo_header.png')
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(__file__), 'icfes_logo.png')
with open(logo_path, "rb") as logo_file:
    logo_base64 = base64.b64encode(logo_file.read()).decode("ascii")

st.markdown(f"""
<div class="dashboard-header">
    <div class="dashboard-brand">
        <img class="dashboard-logo" src="data:image/png;base64,{logo_base64}" alt="Logo ICFES">
        <div class="dashboard-title">
            <h1>Radar ICFES — Contratación Integral</h1>
            <p>Dashboard de gestión contractual · Base Cruzada Maestra Auditada · {years_display}</p>
            <div class="header-badge">{area_display} · {len(df_filtrado):,} contratos</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.info("Vigencia 2026: datos preliminares con corte al 5 de junio de 2026. Sus variaciones se muestran frente al cierre completo de 2025 y no representan periodos equivalentes.")

# ── Guardia de datos vacíos ──
if len(df_filtrado) == 0:
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
    section_header("01", "Comparación anual")
    df_comparacion = df_filtrado.copy()
    annual_metrics = build_annual_metrics(df_comparacion, years)
    if annual_metrics.empty:
        st.warning("No hay contratos para los filtros seleccionados.")
        st.stop()

    available_years = annual_metrics["Annio"].astype(int).tolist()
    if st.session_state.get("active_year") not in available_years:
        st.session_state["active_year"] = max(available_years)

    year_labels = {
        year: f"{year} · Preliminar" if year == 2026 else str(year)
        for year in sorted(available_years)
    }
    valid_labels = list(year_labels.values())
    expected_label = year_labels[st.session_state["active_year"]]
    if st.session_state.get("active_year_control") not in valid_labels:
        st.session_state["active_year_control"] = expected_label
    selected_year_label = st.segmented_control(
        "Vigencia a consultar",
        valid_labels,
        key="active_year_control",
        selection_mode="single",
    )
    selected_year = next(
        (
            year
            for year, label in year_labels.items()
            if label == selected_year_label
        ),
        st.session_state["active_year"],
    )
    st.session_state["active_year"] = int(selected_year)

    active_year = int(st.session_state["active_year"])
    metrics_lookup = annual_metrics.set_index("Annio").to_dict("index")
    current = metrics_lookup[active_year]
    previous = metrics_lookup.get(active_year - 1)
    can_compare = previous is not None

    def card_comparison(metric, formatter, unit="", threshold=0):
        if not can_compare:
            return "Sin año anterior para comparar"
        phrase = comparison_phrase(
            current[metric],
            previous[metric],
            formatter,
            unit,
            threshold,
        )
        if active_year == 2026:
            return phrase.replace(
                "que el año anterior", "que al cierre de 2025"
            )
        return phrase

    execution_status = (
        performance_status(
            "Ejecucion", current["Ejecucion"], previous["Ejecucion"]
        )
        if can_compare and active_year != 2026
        else "neutral"
    )
    delay_status = (
        performance_status(
            "Desfase", current["Desfase"], previous["Desfase"]
        )
        if can_compare and active_year != 2026
        else "neutral"
    )
    cards = [
        {
            "label": "Contratos",
            "value": f"{int(current['Contratos']):,}".replace(",", "."),
            "exact_value": f"{int(current['Contratos'])} contratos",
            "context": "Referencias contractuales únicas",
            "delta": card_comparison(
                "Contratos", lambda value: fmt_decimal_es(value, 0), "contratos", 1
            ),
            "delta_type": "neutral",
        },
        {
            "label": "Valor contratado",
            "value": fmt_cop(current["Valor"]),
            "exact_value": f"${current['Valor']:,.0f} COP",
            "context": "Valor final de los contratos",
            "delta": card_comparison("Valor", fmt_cop_comparison, threshold=1),
            "delta_type": "neutral",
        },
        {
            "label": "PAA planeado",
            "value": fmt_cop(current["PAA"]),
            "exact_value": f"${current['PAA']:,.0f} COP",
            "context": "Valor previsto en el plan anual",
            "delta": card_comparison("PAA", fmt_cop_comparison, threshold=1),
            "delta_type": "neutral",
        },
        {
            "label": "Ejecución del PAA",
            "value": f"{fmt_decimal_es(current['Ejecucion'], 1)}%",
            "exact_value": f"{current['Ejecucion']:.4f}%",
            "context": balance_phrase(current["Balance"]),
            "delta": card_comparison(
                "Ejecucion",
                lambda value: fmt_decimal_es(value, 1),
                "puntos porcentuales",
                0.1,
            ),
            "delta_type": execution_status,
        },
        {
            "label": "Desfase promedio",
            "value": f"{fmt_decimal_es(current['Desfase'], 1)} días",
            "exact_value": f"{current['Desfase']:.4f} días",
            "context": (
                f"{fmt_decimal_es(current['A_Tiempo'], 1)}% firmados a tiempo"
                if not pd.isna(current["A_Tiempo"])
                else "Sin contratos con desfase calculable"
            ),
            "delta": card_comparison(
                "Desfase",
                lambda value: fmt_decimal_es(value, 1),
                "días",
                1,
            ),
            "delta_type": delay_status,
        },
    ]
    render_kpi_cards(cards)

    df_vigencia_activa = df_filtrado[
        df_filtrado["Annio_PAA"].eq(active_year)
    ].copy()
    df = df_vigencia_activa
    active_label = (
        f"{active_year} · Preliminar"
        if active_year == 2026
        else str(active_year)
    )
    period_label = (
        "avance al 5 de junio de 2026"
        if active_year == 2026
        else "vigencia completa"
    )
    st.markdown(
        f'<div class="active-year-badge">Detalle activo: {active_label} · '
        f'{period_label} · {len(df):,} contratos</div>',
        unsafe_allow_html=True,
    )

    trend_col_1, trend_col_2, trend_col_3 = st.columns(3)
    with trend_col_1:
        st.plotly_chart(
            build_summary_chart(
                annual_metrics,
                active_year,
                "Contratos",
                "Contratos por año",
                lambda value: f"{int(value):,}".replace(",", "."),
                lambda value: f"{int(value):,} contratos".replace(",", "."),
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with trend_col_2:
        st.plotly_chart(
            build_summary_chart(
                annual_metrics,
                active_year,
                "Valor",
                "Valor contratado por año",
                fmt_plotly_cop,
                lambda value: f"${value:,.0f} COP",
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )
    with trend_col_3:
        st.plotly_chart(
            build_summary_chart(
                annual_metrics,
                active_year,
                "Desfase",
                "Desfase promedio por año",
                lambda value: f"{fmt_decimal_es(value, 1)} d",
                lambda value: f"{fmt_decimal_es(value, 2)} días",
            ),
            use_container_width=True,
            config={"displayModeBar": False},
        )

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
            question("¿Cuánto representa el valor contratado de cada área?")
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
            desfase_data = area_stats[area_stats['Desfase_Promedio'].notna() & (area_stats['CONTRATO_Area'] != 'No Registra')].sort_values('Desfase_Promedio', ascending=False).head(12)
            colors_d = [COLORS['rojo'] if v > 30 else COLORS['oro'] if v > 10 else COLORS['verde'] for v in desfase_data['Desfase_Promedio']]
            fig = px.bar(desfase_data, y='Nombre_Corto', x='Desfase_Promedio', orientation='h',
                         text_auto='.1f', template=PLOTLY_TEMPLATE,
                         labels={'Nombre_Corto':'', 'Desfase_Promedio':'Desfase Promedio (días)'})
            fig.update_traces(marker_color=colors_d, textposition='outside', hovertemplate='<b>Área:</b> %{y}<br><b>Desfase:</b> %{x} días<extra></extra>')
            fig.update_layout(
                yaxis={
                    'categoryorder': 'array',
                    'categoryarray': list(reversed(desfase_data['Nombre_Corto'].tolist())),
                },
                height=450,
            )
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
        fin = df_comparacion.groupby('Annio_PAA').agg(
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
        question("¿Qué contratos superaron en mayor monto lo previsto en el PAA?")
        top_desv = df[df['KPI_Desviacion_Valor'] > 0].nlargest(10, 'KPI_Desviacion_Valor')[
            ['CONTRATO_Referencia', 'KPI_Desviacion_Valor', 'CONTRATO_Nombre_Contratista', 'CONTRATO_Area']]
        if len(top_desv) > 0:
            top_desv['Nombre_Corto'] = top_desv['CONTRATO_Referencia']
            top_desv['Texto_Valor'] = top_desv['KPI_Desviacion_Valor'].apply(fmt_plotly_cop)
            fig = px.bar(top_desv, y='Nombre_Corto', x='KPI_Desviacion_Valor', orientation='h',
                         text='Texto_Valor', template=PLOTLY_TEMPLATE,
                         color_discrete_sequence=[COLORS['azul']],
                         labels={'KPI_Desviacion_Valor':'Monto sobre el PAA ($COP)', 'Nombre_Corto':''})
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400, clickmode='event+select')
            fig.update_traces(textposition='outside', hovertemplate='<b>Contrato:</b> %{y}<br><b>Monto sobre el PAA:</b> %{text}<extra></extra>')
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
        timing = df_comparacion[
            df_comparacion['KPI_Dias_Desfase'].notna()
        ].copy()
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
        df_mes = df_comparacion[
            df_comparacion['CONTRATO_Fecha_Firma'].notna()
        ].copy()
        if len(df_mes) > 0:
            df_mes['Mes'] = df_mes['CONTRATO_Fecha_Firma'].dt.month
            mc = df_mes.groupby(['Annio_PAA', 'Mes']).size().reset_index(name='Contratos')
            ml = {1:'Ene',2:'Feb',3:'Mar',4:'Abr',5:'May',6:'Jun',7:'Jul',8:'Ago',9:'Sep',10:'Oct',11:'Nov',12:'Dic'}
            mc['Mes_Nombre'] = mc['Mes'].map(ml)
            fig = px.line(mc, x='Mes_Nombre', y='Contratos', color='Annio_PAA', markers=True,
                          labels={'Annio_PAA':'Año', 'Mes_Nombre':'Mes'}, template=PLOTLY_TEMPLATE,
                          color_discrete_sequence=COLORS['palette'][:len(years)])
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
                 custom_data=['CONTRATO_Nombre_Contratista'],
                 color_discrete_sequence=[COLORS['azul']], template=PLOTLY_TEMPLATE,
                 labels={'Nombre':'', 'Valor_Total':'Valor Total ($COP)'})
    fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=500, clickmode='event+select')
    fig.update_traces(textposition='outside', hovertemplate='<b>Contratista:</b> %{y}<br><b>Valor contratado:</b> %{text}<extra></extra>')
    evt2 = st.plotly_chart(fig, use_container_width=True, on_select="rerun", selection_mode="points")

    if evt2 and len(evt2.selection["points"]) > 0:
        point = evt2.selection["points"][0]
        selected_contractor = (
            point.get("customdata", [point.get("y")])[0]
            if isinstance(point.get("customdata"), (list, tuple))
            else point.get("y")
        )
        if selected_contractor:
            df_cont = df[
                df['CONTRATO_Nombre_Contratista'].eq(selected_contractor)
            ]
            st.markdown(f"**Contratos de: {selected_contractor}**")
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
        nat = nat[nat['Tipo'] != 'No registra']
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
        gen = gen[gen['Género'] != 'No registra']
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
            cr = kv.assign(
                Con_adiciones=kv['KPI_Crecimiento_Contractual'].gt(1).astype(int),
                Sin_crecimiento=kv['KPI_Crecimiento_Contractual'].le(1).astype(int),
            ).groupby('Annio_PAA', as_index=False).agg(
                **{
                    'Con adiciones': ('Con_adiciones', 'sum'),
                    'Sin crecimiento': ('Sin_crecimiento', 'sum'),
                }
            )
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
            "Todos", "Menor a $50 millones", "Entre $50 millones y $500 millones",
            "Entre $500 millones y $1.000 millones", "Mayor a $1.000 millones"
        ])

    df_explorador = df.copy()

    if buscar_contrato:
        df_explorador = df_explorador[df_explorador['CONTRATO_Referencia'].str.contains(buscar_contrato, case=False, na=False)]
    if buscar_contratista:
        df_explorador = df_explorador[df_explorador['CONTRATO_Nombre_Contratista'].str.contains(buscar_contratista, case=False, na=False)]
    if rango_valor == "Menor a $50 millones":
        df_explorador = df_explorador[df_explorador['CONTRATO_Valor'] < 50_000_000]
    elif rango_valor == "Entre $50 millones y $500 millones":
        df_explorador = df_explorador[(df_explorador['CONTRATO_Valor'] >= 50_000_000) & (df_explorador['CONTRATO_Valor'] < 500_000_000)]
    elif rango_valor == "Entre $500 millones y $1.000 millones":
        df_explorador = df_explorador[(df_explorador['CONTRATO_Valor'] >= 500_000_000) & (df_explorador['CONTRATO_Valor'] < 1_000_000_000)]
    elif rango_valor == "Mayor a $1.000 millones":
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
                st.markdown(
                    f"**Desfase:** {d['KPI_Dias_Desfase']:.0f} días"
                    if pd.notna(d['KPI_Dias_Desfase'])
                    else "**Desfase:** Sin dato"
                )
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
    El resumen anual muestra una vigencia a la vez mediante cinco indicadores ejecutivos.
    Los gráficos conservan todas las vigencias para facilitar la lectura histórica.
    Los colores verdes indican mejora frente al año anterior y los rojos, deterioro.
    El volumen de contratos, el valor contratado y el PAA se presentan de forma neutral
    porque crecer o disminuir no implica por sí mismo una mejor gestión.
    ''')

    st.markdown("### Cómo se comparan las vigencias")
    st.markdown(
        "- Las vigencias 2022–2025 se presentan con su información completa disponible.\n"
        "- **2026 es preliminar:** corresponde al avance disponible al 5 de junio de 2026. "
        "Sus diferencias se calculan frente al cierre completo de 2025, se muestran en color "
        "neutral y no deben interpretarse como una comparación de periodos equivalentes.\n"
        "- **A tiempo:** porcentaje de contratos con desfase calculable que fueron firmados "
        "en la fecha planeada o antes.\n"
        "- Los contratos sin fecha PAA verificable o con una fecha ambigua se excluyen "
        "únicamente de los indicadores de oportunidad; no se les imputa una fecha."
    )
    
    st.markdown("### 1. Fórmulas de Cálculo de Indicadores (KPIs)")
    
    st.markdown("**1.1 Diferencia frente al PAA (`KPI_Desviacion_Valor`)**")
    st.markdown("Compara el valor contratado con lo previsto en el PAA.")
    st.latex(r"\text{Desviación} = \text{CONTRATO\_Valor} - \text{Valor\_Esperado\_PAA}")
    st.markdown("- **Si < 0:** valor contratado por debajo del PAA; no se interpreta automáticamente como ahorro.")
    st.markdown("- **Si > 0:** valor contratado por encima del PAA.")
    st.markdown("- **Fuente:** Cruce estricto validado por ID de proceso o justificación PAA.")

    st.markdown("**1.2 Crecimiento Contractual (`KPI_Crecimiento_Contractual`)**")
    st.markdown("Evalúa la ocurrencia de adiciones presupuestales sobre el monto inicial firmado.")
    st.latex(r"\text{Crecimiento} = \left( \frac{\text{CONTRATO\_Valor}}{\text{CONTRATO\_Valor\_Inicial}} \right)")
    st.markdown("- **Si = 1.0:** Ejecución exacta sin adiciones monetarias.")
    st.markdown("- **Si > 1.0:** El contrato sufrió adiciones (ej. 1.25 representa un incremento del 25% sobre la base).")
    
    st.markdown("**1.3 Demora frente al plan (`KPI_Dias_Desfase`)**")
    st.markdown("Mide los días entre la fecha prevista en el PAA y la firma del contrato.")
    st.latex(r"\text{Desfase (días)} = \text{Fecha\_Firma\_Contrato} - \text{Fecha\_Estimada\_PAA}")
    st.markdown("- **Si > 0:** Retraso administrativo (se firmó post-calendario).")
    st.markdown("- **Si = 0:** El contrato se firmó en la fecha planeada.")
    st.markdown("- **Si < 0:** El contrato se firmó antes de la fecha planeada; los días anticipados se conservan sin truncarlos.")
    st.markdown("---")

    st.markdown("### 2. Diccionario de Datos Estandarizado")
    
    diccionario_data = [
        {"Variable": "Annio_PAA", "Definición Estricta": "Vigencia fiscal oficial identificada para el contrato o el PAA cruzado (2022 a 2026)."},
        {"Variable": "CONTRATO_Area", "Definición Estricta": "Dependencia del ICFES asignada (homologada y purgada de variaciones ortográficas de SECOP)."},
        {"Variable": "CONTRATO_Valor", "Definición Estricta": "El valor monetario TOTAL FINAL del contrato, incluyendo adiciones (si las hubo). Es el número de facturación real."},
        {"Variable": "CONTRATO_Valor_Inicial", "Definición Estricta": "El valor oficial por el cual se sancionó y firmó el contrato en su primer día (sin adiciones)."},
        {"Variable": "Valor_Esperado_PAA", "Definición Estricta": "Tope presupuestal inmovilizado por planeación para llevar a cabo el proceso de la necesidad."},
        {"Variable": "CONTRATO_Referencia", "Definición Estricta": "Identificador alfanumérico único oficial de SECOP que previene la existencia de contratos duplicados o fantasmas en el dashboard."},
        {"Variable": "CONTRATO_Estado", "Definición Estricta": "Estado contractual homologado: Anulado, En ejecución, Firmado, Liquidado, Suspendido, Terminado o No Registra."},
        {"Variable": "CONTRATO_Naturaleza_Juridica", "Definición Estricta": "Tipo de contratista homologado como Persona natural, Persona jurídica o No registra."}
    ]

    st.dataframe(pd.DataFrame(diccionario_data), use_container_width=True, hide_index=True)
    st.markdown("<br>", unsafe_allow_html=True)

# Descarga
csv = df_explorador.to_csv(index=False, encoding='utf-8-sig')
nombre_archivo = f"datos_icfes_{'global' if vista_global else opcion_area.replace(' ','_')[:30]}.csv"
st.download_button(label="Descargar datos filtrados (CSV)", data=csv,
                   file_name=nombre_archivo, mime="text/csv")

st.markdown('<div class="dashboard-footer">Radar ICFES · Dashboard Integral de Contratación · Base Cruzada Maestra Auditada · 2022–2026</div>', unsafe_allow_html=True)
