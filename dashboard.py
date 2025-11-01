import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px  # Importamos Plotly para gráficos interactivos

# --- 1. Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard de Producción",
    layout="wide"
)

# --- 2. Carga de Datos y Caching ---
@st.cache_data
def load_data():
    """
    Esta función se conecta a Google Sheets, extrae y limpia los datos.
    El decorador @st.cache_data asegura que esto solo se ejecute UNA VEZ.
    """
    print("Iniciando carga de datos (esto solo debe aparecer una vez)...")

    try:
        from config import sheet_url, credentials_file
    except ImportError:
        st.error(
            "No se encontró el archivo 'config.py'. Por favor, renombra 'config.py.example' a 'config.py' y añade tus credenciales.")
        return pd.DataFrame()

    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
        client = gspread.authorize(creds)
    except FileNotFoundError:
        st.error(
            f"No se encontró el archivo de credenciales: '{credentials_file}'. Asegúrate de que esté en la carpeta.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error de autenticación: {e}")
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

        # Convertir la fecha a un objeto 'date' para el filtro
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

    # Filtro de Rango de Fechas
    fecha_min = df['FECHA'].min()
    fecha_max = df['FECHA'].max()

    # st.sidebar.date_input crea el widget de calendario
    fecha_inicio, fecha_fin = st.sidebar.date_input(
        "Selecciona el Rango de Fechas",
        value=[fecha_min, fecha_max],  # Valor por defecto 
        min_value=fecha_min,
        max_value=fecha_max
    )

    # Filtro de Supervisor (Multiselect)
    opciones_supervisor = sorted(df['SUPERVISOR DE PRODUCCIÓN'].unique())
    supervisor_seleccionado = st.sidebar.multiselect(
        "Filtrar por Supervisor",
        options=opciones_supervisor,
        default=opciones_supervisor  # Por defecto, selecciona todos
    )

    # Filtro de Producto (Multiselect)
    opciones_producto = sorted(df['PRODUCTO'].unique())
    producto_seleccionado = st.sidebar.multiselect(
        "Filtrar por Producto",
        options=opciones_producto,
        default=opciones_producto  # Por defecto, selecciona todos
    )

    # --- 5. Aplicación de Filtros al DataFrame ---

    # Filtramos el DataFrame 'df' basado en las selecciones del usuario
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
        st.success(f"Mostrando {len(df_filtrado)} registros de {len(df)} totales.")

        # Aquí es donde pondremos nuestros gráficos en el siguiente paso
        st.subheader("Datos Filtrados")
        columnas_a_mostrar = [
            'PRODUCTO',
            'LOTE DE PRODUCCIÓN',
            'CANTIDAD (COSTALES)',
            'SUPERVISOR DE PRODUCCIÓN'
        ]

        # Muestra el dataframe solo con esas columnas
        st.dataframe(df_filtrado[columnas_a_mostrar])