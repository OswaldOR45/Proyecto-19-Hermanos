"""
En este script generamos el Dashboard para una mejor visualización de los análisis y los resultados obtenidos, a este script
se le adjuntarán 2 modulos, esto debido a la fase 2 de el proyecto, donde ya se esperan datos de EMBARQUES, entonces ya
harán cálculos de PEPS, entonces aligeraré la carga y limpieza de código de este script, con ayuda de etl.py y analysis.py


Hecho por Oswaldo Reynoso 01/11/2025
"""

import streamlit as st
import pandas as pd
import plotly.express as px
# Importamos nuestra función de "fontanería" desde el nuevo módulo
from etl import load_data

# --- 1. Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Producción",
    layout="wide"
)

# --- 3. Ejecución Principal del Dashboard ---

st.title("Dashboard de Producción - 19 Hermanos Pet Food")

# Llamamos a la función load_data() que ahora vive en etl.py
# Gracias al caché, esto solo se ejecuta una vez.
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
        # Métricas simples que tu gerente pidió (Volumen y Frecuencia)
        total_costales = int(df_filtrado['CANTIDAD (COSTALES)'].sum())
        total_lotes = int(df_filtrado['CANTIDAD (COSTALES)'].count())
        costales_por_lote = int(total_costales / total_lotes) if total_lotes > 0 else 0

        # Mostramos los KPIs en 3 columnas
        col1, col2, col3 = st.columns(3)
        col1.metric("Costales Totales Producidos", f"{total_costales:,}")
        col2.metric("Total de Lotes Registrados", f"{total_lotes:,}")
        col3.metric("Promedio de Costales por Lote", f"{costales_por_lote:,}")

        st.markdown("---")  # Una línea divisoria

        # --- 8. Visualizaciones del Dashboard ---
        col1, col2 = st.columns(2)  # Creamos dos columnas para los gráficos

        # Gráfico 1: Gráfico de Pastel por Producto (Lo que pidió el director)
        with col1:
            st.subheader("Producción por Producto")
            # Agrupamos por producto y sumamos
            prod_por_producto = df_filtrado.groupby('PRODUCTO')['CANTIDAD (COSTALES)'].sum().reset_index()
            prod_por_producto = prod_por_producto.sort_values(by='CANTIDAD (COSTALES)', ascending=False)

            # Creamos el gráfico de pastel con Plotly
            fig_pie = px.pie(
                prod_por_producto.head(10),  # Tomamos el Top 10
                names='PRODUCTO',
                values='CANTIDAD (COSTALES)',
                title='Top 10 Productos por Producción'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Gráfico 2: Gráfico de Barras por Supervisor
        with col2:
            st.subheader("Producción por Supervisor")
            # Agrupamos por supervisor y sumamos
            prod_por_supervisor = df_filtrado.groupby('SUPERVISOR DE PRODUCCIÓN')[
                'CANTIDAD (COSTALES)'].sum().reset_index()
            prod_por_supervisor = prod_por_supervisor.sort_values(by='CANTIDAD (COSTALES)', ascending=False)

            # Creamos el gráfico de barras con Plotly
            fig_bar_super = px.bar(
                prod_por_supervisor,
                x='SUPERVISOR DE PRODUCCIÓN',
                y='CANTIDAD (COSTALES)',
                title='Producción Total por Supervisor'
            )
            st.plotly_chart(fig_bar_super, use_container_width=True)

        st.markdown("---")

        # Gráfico 3: Tendencia de Producción (Gráfico de Líneas)
        st.subheader("Tendencia de Producción en el Tiempo")
        # Agrupamos por fecha (usamos la columna FECHA que ya creamos)
        prod_por_fecha = df_filtrado.groupby('FECHA')['CANTIDAD (COSTALES)'].sum().reset_index()

        fig_line = px.line(
            prod_por_fecha,
            x='FECHA',
            y='CANTIDAD (COSTALES)',
            title='Producción Total por Día'
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # --- 9. TABLA DE DATOS (OPCIONAL) ---
        st.markdown("---")
        st.subheader("Detalle de Registros Filtrados")

        # Usamos un expander para que la tabla no ocupe espacio por defecto
        with st.expander("Ver/Ocultar Tabla de Datos"):
            # Define las columnas que tu gerente quería ver
            columnas_a_mostrar = [
                'PRODUCTO',
                'LOTE DE PRODUCCIÓN',
                'CANTIDAD (COSTALES)',
                'SUPERVISOR DE PRODUCCIÓN'
            ]

            # Muestra el dataframe solo con esas columnas
            st.dataframe(df_filtrado[columnas_a_mostrar], use_container_width=True)