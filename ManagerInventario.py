#Realizado por Oswaldo Reynoso Robles Practicante IT el 11 de octubre de 2025

#Script donde se obtienen los datos de ENTRADAS, SALIDAS e Inventario de la empresa 19 Hermanos planta Pet Food de:
# https://docs.google.com/spreadsheets/d/1U42KozvOiQLWoi0O_6Ij17Vd6Yy71NBVHraIrue9OS8/edit?gid=0#gid=0

#Se busca realizar un procesamiento de esos datos, con la finalidad de obtener reslutados, para tomas de decisiones
#El archivo contiene las siguientes pestañas y sus datos utilizables para este proyecto:

#Pestaña: ENTRADAS, Datos: TIMESTAMP, PRODUCTO, LOTE DE PRODUCCIÓN, CANTIDAD (COSTALES), TURNO, OPERADOR DE EMPAQUE, SUPERVISOR DE PRODUCCIÓN, REGISTRADO POR
#Pestaña: SALIDAS, Datos: TIMESTAMP, PRODUCTO, LOTE DE SALIDA, CANTIDAD (COSTALES), CLIENTE, NUM.ORDEN DE SALIDA, SUPERVISOR DE EMBARQUE, REGISTRADO POR
#Pestaña: INVENTARIO/STOCK, Datos: Producto, LOTE, TOTAL DE ENTRADAS, TOTAL DE SALIDAS, STOCK(E-S)


# --- CONFIGURACIÓN Y CONEXIÓN ---
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import matplotlib.pyplot as plt

print("Librerías importadas correctamente.")

# --- Autenticación ---
# Define el alcance de los permisos.
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# Apunta al archivo de credenciales JSON.
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
# Autoriza al cliente de gspread.
client = gspread.authorize(creds)
print("Autenticación con Google exitosa.")

# --- Acceso al Archivo ---
sheet_url = "https://docs.google.com/spreadsheets/d/1U42KozvOiQLWoi0O_6Ij17Vd6Yy71NBVHraIrue9OS8/edit#gid=0"

try:
    # Abre la hoja de cálculo usando su URL.
    spreadsheet = client.open_by_url(sheet_url)
    # Selecciona la pestaña 'ENTRADAS'.
    sheet_entradas = spreadsheet.worksheet('ENTRADAS')

    print(f"Conexión exitosa con la hoja '{spreadsheet.title}'.")
    print(f"Pestaña '{sheet_entradas.title}' encontrada.")

#ESTE PROYECTO SE LLEVARÁ A CABO UTLIZANDO EL METODO DE ANALISIS DE DATOS LLAMADO ETL
#QUE SIGNIFICA EXTRACT, TRANSFORM, LOAD, EN ESTOS MOMENTOS COMENZAREMOS CON EL PASO 1:
#QUE ES EXTRAER LOS DATOS DE LA SPREADSHEET E IDENTIFICARLOS

    print("\n Iniciando extracción de datos... ")
    data = sheet_entradas.get_values()
    if len(data) <= 1:
        print(" La hoja esta vacía, o solo tiene los encabezados. ")
    else:
        df = pd.DataFrame(data[1:],columns=data[0])
        print(f"Datos extraídos. Se encontraron {len(df)} registros.")

#Etapa de limpieza de datos, ya que se realizó una prueba y python toma en cuenta: CANTIDAD DE COSTALES
#y el TIMESTAMP como objeto, no como su tipo de dato correspondiente

        # Convertir CANTIDAD (COSTALES) a números
        # 'errors=coerce' convierte cualquier texto que NO sea un número en 'NaN' (Not a Number)
        # Esto evita que el script falle si hay un error de dedo (ej. "1O0" en lugar de "100")
        df['CANTIDAD (COSTALES)'] = pd.to_numeric(df['CANTIDAD (COSTALES)'], errors='coerce')
        # Convertir TIMESTAMP a fechas
        # Especificamos el formato exacto de tu hoja (día/mes/año Hora:Min:Seg) para evitar confusiones
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], format='%d/%m/%Y %H:%M:%S')
        # Manejar filas con errores
        # Si hubo algún error en la conversión (ej. un texto en 'CANTIDAD'), esa fila se eliminará.
        original_rows = len(df)
        df = df.dropna(subset=['CANTIDAD (COSTALES)'])
        new_rows = len(df)
        if original_rows > new_rows:
            print(
                f"Se eliminaron {original_rows - new_rows} filas por tener datos no numéricos en 'CANTIDAD (COSTALES)'.")

        print("Limpieza de datos completada...")

        print("\n--- Información y tipos de datos (Después de limpiar) ---")
        df.info()

        # 1. Análisis por Turno
        productividad_por_turno = df.groupby('TURNO')['CANTIDAD (COSTALES)'].sum()
        print("\n--- Resultados: Productividad Total por Turno ---")
        print(productividad_por_turno)

        # 2. Análisis por Producto
        productividad_por_producto = df.groupby('PRODUCTO')['CANTIDAD (COSTALES)'].sum().sort_values(ascending=False)
        print("\n--- Resultados: Productividad Total por Producto ---")
        print(productividad_por_producto)

        # 3. Análisis por Operador
        # Usamos 'OPERADOR DE EMPAQUE'
        productividad_por_operador = df.groupby('OPERADOR DE EMPAQUE')['CANTIDAD (COSTALES)'].sum().sort_values(
            ascending=False)
        print("\n--- Resultados: Productividad Total por Operador ---")
        print(productividad_por_operador)

        # 4. Análisis por Supervisor
        productividad_por_supervisor = df.groupby('SUPERVISOR DE PRODUCCIÓN')['CANTIDAD (COSTALES)'].sum().sort_values(
            ascending=False)
        print("\n--- Resultados: Productividad Total por Supervisor ---")
        print(productividad_por_supervisor)

        print("\n--- INICIANDO ANÁLISIS ESTADÍSTICO AVANZADO ---")

        # Definimos las estadísticas que queremos calcular
        stats_a_calcular = ['sum', 'count', 'mean', 'std', 'min', 'max']

        # 1. Análisis estadístico por Turno
        stats_por_turno = df.groupby('TURNO')['CANTIDAD (COSTALES)'].agg(stats_a_calcular)
        print("\n--- Resultados (Avanzados): Estadísticas por Turno ---")
        print(stats_por_turno.round(2))

        # 2. Análisis estadístico por Producto
        stats_por_producto = df.groupby('PRODUCTO')['CANTIDAD (COSTALES)'].agg(stats_a_calcular).sort_values(by='sum', ascending=False)
        print("\n--- Resultados (Avanzados): Estadísticas por Producto ---")
        print(stats_por_producto.round(2))

        # 3. Análisis estadístico por Operador
        stats_por_operador = df.groupby('OPERADOR DE EMPAQUE')['CANTIDAD (COSTALES)'].agg(stats_a_calcular).sort_values(
            by='sum', ascending=False)
        print("\n--- Resultados (Avanzados): Estadísticas por Operador ---")
        print(stats_por_operador.round(2))

        # 4. Análisis estadístico por Supervisor
        stats_por_supervisor = df.groupby('SUPERVISOR DE PRODUCCIÓN')['CANTIDAD (COSTALES)'].agg(
            stats_a_calcular).sort_values(by='sum', ascending=False)
        print("\n--- Resultados (Avanzados): Estadísticas por Supervisor ---")
        print(stats_por_supervisor.round(2))

        # ANÁLISIS DE TENDENCIA (SERIE DE TIEMPO) ---
        print("\n--- INICIANDO ANÁLISIS DE TENDENCIA ---")
        df_temporal = df.set_index('TIMESTAMP')

        # 'W' = Semanalmente (Weekly). Agrupará todos los registros por semana y los sumará.
        # 'D' (Diario) o 'M' (Mensual)
        produccion_semanal = df_temporal.resample('D')['CANTIDAD (COSTALES)'].sum()

        print("\n--- Resultados: Producción Total por Semana ---")
        print(produccion_semanal)
        print("\n Análisis de tendencia completado.")

        # --- PASO 5: VISUALIZACIÓN ---
        print("\n--- INICIANDO VISUALIZACIÓN ---")

        # Gráfico 1: Productividad por Turno
        plt.figure(figsize=(10, 6))
        productividad_por_turno.plot(kind='bar', color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        plt.title('Productividad Total por Turno', fontsize=16, fontweight='bold')
        plt.xlabel('Número de Turno', fontsize=12)
        plt.ylabel('Cantidad de Costales Producidos', fontsize=12)
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Gráfico 2: Top 10 Productos
        plt.figure(figsize=(12, 8))
        productividad_por_producto.head(10).plot(kind='barh', color='purple')
        plt.title('Productos por Producción Total', fontsize=16, fontweight='bold')
        plt.xlabel('Cantidad de Costales Producidos', fontsize=12)
        plt.ylabel('Producto', fontsize=12)
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Gráfico 3: Top 10 Operadores
        plt.figure(figsize=(12, 8))
        productividad_por_operador.head(10).plot(kind='barh', color='teal')
        plt.title('Operadores por Producción Total', fontsize=16, fontweight='bold')
        plt.xlabel('Cantidad de Costales Producidos', fontsize=12)
        plt.ylabel('Operador', fontsize=12)
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Gráfico 4: Productividad por Supervisor
        plt.figure(figsize=(12, 8))
        productividad_por_supervisor.plot(kind='barh', color='brown')
        plt.title('Productividad Total por Equipo de Supervisor', fontsize=16, fontweight='bold')
        plt.xlabel('Cantidad de Costales Producidos', fontsize=12)
        plt.ylabel('Supervisor', fontsize=12)
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Gráfico 5: Tendencia de Producción Semanal
        plt.figure(figsize=(12, 7))
        produccion_semanal.plot(kind='line', marker='o', color='red', linewidth=2)
        plt.title('Tendencia de Producción Semanal', fontsize=16, fontweight='bold')
        plt.xlabel('Semana', fontsize=12)
        plt.ylabel('Cantidad de Costales Producidos', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        #Gráficos Estadísticos ---

        # Gráfico 6: Eficiencia por Supervisor (Lote Promedio)
        plt.figure(figsize=(12, 8))
        stats_por_supervisor['mean'].sort_values().plot(kind='barh', color='blue')  # Usamos la columna 'mean'
        plt.title('Eficiencia por Supervisor (Lote Promedio)', fontsize=16, fontweight='bold')
        plt.xlabel('Cantidad Promedio de Costales por Lote', fontsize=12)
        plt.ylabel('Supervisor', fontsize=12)
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Gráfico 7: Consistencia por Supervisor (Desviación Estándar)
        plt.figure(figsize=(12, 8))
        stats_por_supervisor['std'].sort_values().plot(kind='barh', color='green')  # Usamos la columna 'std'
        plt.title('Consistencia por Supervisor (Desviación Estándar)', fontsize=16, fontweight='bold')
        plt.xlabel('Variabilidad de Costales (Barras más bajas son mejores)', fontsize=12)
        plt.ylabel('Supervisor', fontsize=12)
        plt.gca().invert_yaxis()
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Gráfico 8: Eficiencia por Turno (Lote Promedio)
        plt.figure(figsize=(10, 6))
        stats_por_turno['mean'].plot(kind='bar', color='orange')  # Usamos la columna 'mean' de stats_por_turno
        plt.title('Eficiencia por Turno (Lote Promedio)', fontsize=16, fontweight='bold')
        plt.xlabel('Número de Turno', fontsize=12)
        plt.ylabel('Cantidad Promedio de Costales por Lote', fontsize=12)
        plt.xticks(rotation=0)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()

        print("Gráficos generados. Mostrando en nuevas ventanas...")
        plt.show()

except Exception as e:
    print("\n OCURRIÓ UN ERROR ")
    print(f"\nError detallado: {e}")