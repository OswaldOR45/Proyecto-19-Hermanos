import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

# --- 1. Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Producción",
    layout="wide"
)

# --- 2. Carga de Datos y Caching ---
@st.cache_data
def load_data():
    print("Iniciando carga de datos (esto solo debe aparecer una vez)...")

    try:
        sheet_url = st.secrets["SHEET_URL"]
        GCP_CREDS = st.secrets["gcp_service_account"]
    except Exception as e:
        st.error(f" Error al leer los secrets de Streamlit. Asegúrate de configurarlos en el deploy. Detalle: {e}")
        return pd.DataFrame()

    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(GCP_CREDS, scope)
        client = gspread.authorize(creds)
    except Exception as e:
        st.error(f"Error de autenticación con Google. Revisa tus credenciales en st.secrets. Detalle: {e}")
        return pd.DataFrame()

    try:
        spreadsheet = client.open_by_url(sheet_url)
        sheet_entradas = spreadsheet.worksheet('ENTRADAS')
        data = sheet_entradas.get_all_values()

        if len(data) <= 1:
            st.warning("La hoja 'ENTRADAS' está vacía.")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
    except Exception as e:
        st.error(f"Error al leer la hoja de Google: {e}")
        return pd.DataFrame()

    try:
        df['CANTIDAD (COSTALES)'] = pd.to_numeric(df['CANTIDAD (COSTALES)'], errors='coerce')
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%d/%m/%Y %H:%M:%S')
        df = df.dropna(subset=['CANTIDAD (COSTALES)'])
        df['FECHA'] = df['TIMESTAMP'].dt.date
        print("...Carga de datos completada.")
        return df

    except Exception as e:
        st.error(f"Error durante la limpieza de datos: {e}")
        return pd.DataFrame()


# --- 3. Ejecución Principal del Dashboard ---

st.title("Dashboard de Producción - 19 Hermanos Pet Food")
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