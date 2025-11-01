"""
En este script generamos el Dashboard para una mejor visualización de los análisis y los resultados obtenidos, a este script
se le adjuntarán 2 modulos, esto debido a la fase 2 de el proyecto, donde ya se esperan datos de EMBARQUES, entonces ya
harán cálculos de PEPS, entonces aligeraré la carga y limpieza de código de este script, con ayuda de etl.py y analysis.py


Hecho por Oswaldo Reynoso 01/11/2025
"""

import streamlit as st
import pandas as pd
from etl import load_data
from analysis import (
    calculate_kpis,
    generate_pie_chart,
    generate_bar_chart,
    generate_line_chart
)

# --- 1. Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Producción",
    layout="wide"
)

# --- 3. Ejecución Principal del Dashboard ---

st.title("Dashboard de Producción - 19 Hermanos Pet Food")

# 1. CARGAR DATOS (desde etl.py)
df = load_data()

if df.empty:
    st.error("No se pudieron cargar los datos. Revisa los mensajes de error.")
else:
    # --- 4. Barra Lateral de Filtros ---
    st.sidebar.header("Filtros del Dashboard")

    fecha_min = df['FECHA'].min()
    fecha_max = df['FECHA'].max()

    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el Rango de Fechas",
        value=[fecha_min, fecha_max],
        min_value=fecha_min,
        max_value=fecha_max
    )

    opciones_supervisor = sorted(df['SUPERVISOR DE PRODUCCIÓN'].unique())
    supervisor_seleccionado = st.sidebar.multiselect(
        "Filtrar por Supervisor",
        options=opciones_supervisor,
        default=opciones_supervisor
    )

    opciones_producto = sorted(df['PRODUCTO'].unique())
    producto_seleccionado = st.sidebar.multiselect(
        "Filtrar por Producto",
        options=opciones_producto,
        default=opciones_producto
    )

    # --- 5. Aplicación de Filtros al DataFrame ---

    df_filtrado = df[
        (df['FECHA'] >= fecha_inicio) &
        (df['FECHA'] <= fecha_fin) &
        (df['SUPERVISOR DE PRODUCCIÓN'].isin(supervisor_seleccionado)) &
        (df['PRODUCTO'].isin(producto_seleccionado))
    ]

    # --- 6. Mostrar el Dashboard ---

    if df_filtrado.empty:
        st.warning("No se encontraron datos con los filtros seleccionados.")
    else:
        # --- 7. KPIs Principales ---
        # 2. CALCULAR KPIs (desde analysis.py)
        total_costales, total_lotes, costales_por_lote = calculate_kpis(df_filtrado)

        col1, col2, col3 = st.columns(3)
        col1.metric("Costales Totales Producidos", f"{total_costales:,}")
        col2.metric("Total de Lotes Registrados", f"{total_lotes:,}")
        col3.metric("Promedio de Costales por Lote", f"{costales_por_lote:,}")

        st.markdown("---")  # Una línea divisoria

        # --- 8. Visualizaciones del Dashboard ---
        col1, col2 = st.columns(2)  # Creamos dos columnas para los gráficos

        with col1:
            st.subheader("Producción por Producto")
            # 3. GENERAR GRÁFICO 1 (desde analysis.py)
            fig_pie = generate_pie_chart(df_filtrado)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            st.subheader("Producción por Supervisor")
            # 4. GENERAR GRÁFICO 2 (desde analysis.py)
            fig_bar_super = generate_bar_chart(df_filtrado)
            st.plotly_chart(fig_bar_super, use_container_width=True)

        st.markdown("---")

        st.subheader("Tendencia de Producción en el Tiempo")
        # 5. GENERAR GRÁFICO 3 (desde analysis.py)
        fig_line = generate_line_chart(df_filtrado)
        st.plotly_chart(fig_line, use_container_width=True)

        # --- 9. TABLA DE DATOS (OPCIONAL) ---
        st.markdown("---")
        st.subheader("Detalle de Registros Filtrados")

        with st.expander("Ver/Ocultar Tabla de Datos"):
            columnas_a_mostrar = [
                'PRODUCTO',
                'LOTE DE PRODUCCIÓN',
                'CANTIDAD (COSTALES)',
                'SUPERVISOR DE PRODUCCIÓN'
            ]
            st.dataframe(df_filtrado[columnas_a_mostrar], use_container_width=True)