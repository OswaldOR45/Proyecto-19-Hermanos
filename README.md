# Proyecto: Análisis de Producción de Inventario (19 Hermanos)

Este proyecto es un script de Python que aplica un proceso ETL (Extract, Transform, Load) para analizar datos de producción de una planta de Pet Food, conectándose directamente a una base de datos en Google Sheets.

## Descripción
El script se conecta de forma segura a la API de Google Sheets, extrae todos los registros de producción, los limpia y transforma (convirtiendo tipos de datos y manejando errores), y finalmente carga los datos en un DataFrame de `pandas` para un análisis profundo.

## Capacidades de Análisis
El script genera un conjunto completo de análisis sobre la eficiencia operativa de la planta:

* **Análisis de Productividad (Sumas):**
    * Producción total por Turno.
    * Producción total por Producto (Top 10).
    * Producción total por Operador (Top 10).
    * Producción total por Supervisor.

* **Análisis Estadístico Avanzado (Eficiencia y Consistencia):**
    * Calcula métricas clave (`sum`, `count`, `mean`, `std`, `min`, `max`) para cada categoría.
    * Permite identificar no solo *quién* produce más, sino *quién* es más eficiente (lote promedio) y consistente (desviación estándar).

* **Análisis de Tendencias (Series de Tiempo):**
    * Genera un gráfico de líneas que muestra la producción total día a día, permitiendo identificar patrones.

## Herramientas Utilizadas
* **Python 3**
* **Pandas:** Para la manipulación y análisis de datos.
* **Matplotlib:** Para la visualización y generación de gráficos.
* **gspread & oauth2client:** Para la autenticación segura y conexión con la API de Google Sheets.

## Ejecución
Para ejecutar este script, se requiere un archivo `credentials.json` de una cuenta de servicio de Google Cloud que tenga acceso a la hoja de cálculo de destino (este archivo está excluido del repositorio por seguridad).