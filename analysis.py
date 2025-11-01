"""
Único objetivo es hacer calculos analíticos para mandarlos a Dashboard.py (Obtiene datos de etl.py)
Este script es parte de la modularización en la fase 1 después de que se obtengan los datos de embarques,para una mejor
modularización y performance, y un código mas limpio

Hecho por Oswaldo Reynoso 01/11/2025
"""

import pandas as pd
import plotly.express as px

# --- Funciones de Cálculo de KPIs ---
def calculate_kpis(df_filtrado):

    if df_filtrado.empty:
        return 0, 0, 0

    total_costales = int(df_filtrado['CANTIDAD (COSTALES)'].sum())
    total_lotes = int(df_filtrado['CANTIDAD (COSTALES)'].count())
    costales_por_lote = int(total_costales / total_lotes) if total_lotes > 0 else 0

    return total_costales, total_lotes, costales_por_lote


# --- Funciones de Generación de Gráficos ---

def generate_pie_chart(df_filtrado):

    prod_por_producto = df_filtrado.groupby('PRODUCTO')['CANTIDAD (COSTALES)'].sum().reset_index()
    prod_por_producto = prod_por_producto.sort_values(by='CANTIDAD (COSTALES)', ascending=False)

    fig_pie = px.pie(
        prod_por_producto.head(10),  # Tomamos el Top 10
        names='PRODUCTO',
        values='CANTIDAD (COSTALES)',
        title='Top 10 Productos por Producción'
    )
    return fig_pie


def generate_bar_chart(df_filtrado):
    prod_por_supervisor = df_filtrado.groupby('SUPERVISOR DE PRODUCCIÓN')['CANTIDAD (COSTALES)'].sum().reset_index()
    prod_por_supervisor = prod_por_supervisor.sort_values(by='CANTIDAD (COSTALES)', ascending=False)

    fig_bar_super = px.bar(
        prod_por_supervisor,
        x='SUPERVISOR DE PRODUCCIÓN',
        y='CANTIDAD (COSTALES)',
        title='Producción Total por Supervisor'
    )
    return fig_bar_super


def generate_line_chart(df_filtrado):

    prod_por_fecha = df_filtrado.groupby('FECHA')['CANTIDAD (COSTALES)'].sum().reset_index()

    fig_line = px.line(
        prod_por_fecha,
        x='FECHA',
        y='CANTIDAD (COSTALES)',
        title='Producción Total por Día'
    )
    return fig_line