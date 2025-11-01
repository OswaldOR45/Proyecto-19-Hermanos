"""
SCRIPT DONDE SE HARÁ TODA LA EXTRACCIÓN, TRANSFORMACIÓN Y CARGA DE DATOS.

¿Qué diferencia hay de ManagerInventario a etl?

ManagerInventario lo dejaremos unicamente para hacer pruebas, ya que tras seguir el plan de analisis decidí modularizar
el proyecto agregando 2 scripts más

-etl.py: Aqui lo llamaremos como el cuarto de maquinas, hará toda la importación, transformación y carga

Hecho por Oswaldo Reynoso 01/11/2025
"""
import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


# --- 2. Carga de Datos y Caching ---
@st.cache_data
def load_data():
    print("Iniciando carga de datos (esto solo debe aparecer una vez)...")

    try:
        sheet_url = st.secrets["sheet_url"]
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

    # --- INICIO DE LA LÓGICA DE EXTRACCIÓN (FASE 2) ---
    # Por ahora, solo leemos ENTRADAS.
    # En el futuro, aquí es donde leeremos SALIDAS e INVENTARIO.

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

    # --- INICIO DE LA LÓGICA DE TRANSFORMACIÓN (FASE 2) ---
    # Por ahora, solo limpiamos ENTRADAS.

    try:
        df['CANTIDAD (COSTALES)'] = pd.to_numeric(df['CANTIDAD (COSTALES)'], errors='coerce')
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%d/%m/%Y %H:%M:%S')
        df = df.dropna(subset=['CANTIDAD (COSTALES)'])
        df['FECHA'] = df['TIMESTAMP'].dt.date
        print("...Carga de datos completada.")

        # En el futuro, aquí retornaremos un diccionario con todos los dataframes
        # return {"entradas": df, "salidas": df_salidas, ...}
        return df

    except Exception as e:
        st.error(f"Error durante la limpieza de datos: {e}")
        return pd.DataFrame()
