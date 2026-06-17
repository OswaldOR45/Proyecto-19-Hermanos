# 📊 Dashboard de Producción — 19 Hermanos Pet Food

Plataforma de análisis de producción para una planta de alimento para mascotas. Aplica un proceso **ETL** sobre datos de producción almacenados en Google Sheets y los presenta en un **dashboard interactivo de Streamlit** con KPIs, filtros dinámicos y visualizaciones.

El proyecto evolucionó de un script exploratorio monolítico a una **arquitectura modular** (extracción, análisis y presentación desacoplados), pensada para crecer hacia el control de inventario completo (entradas, salidas y stock con método PEPS/FIFO).

![Status](https://img.shields.io/badge/status-en%20desarrollo%20activo-success)
![Python](https://img.shields.io/badge/Python-3-3776AB)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B)
![Pandas](https://img.shields.io/badge/Pandas-data-150458)
![Data](https://img.shields.io/badge/fuente-Google%20Sheets%20API-0F9D58)

---

## 📌 El problema

La producción de la planta se registraba en Google Sheets, pero los datos en crudo no permitían responder preguntas de negocio de forma ágil:

- ¿Qué turno, producto, operador o supervisor produce más?
- ¿Quién es más **eficiente** (mayor lote promedio) y más **consistente** (menor variabilidad)?
- ¿Cómo evoluciona la producción día a día?

Este proyecto convierte esa hoja en una herramienta de decisión: extrae y limpia los datos automáticamente, calcula métricas y los muestra en un dashboard filtrable, sin que nadie tenga que tocar fórmulas ni tablas dinámicas.

---

## ✨ Características principales

- **Pipeline ETL** sobre Google Sheets: extracción vía API, limpieza y tipado de datos (conversión de cantidades a numérico, parseo de fechas, descarte de filas inválidas con `errors='coerce'`).
- **Dashboard interactivo (Streamlit)** con:
  - **KPIs**: costales totales producidos, total de lotes y promedio de costales por lote.
  - **Filtros dinámicos** por rango de fechas, supervisor y producto.
  - **Gráficos interactivos (Plotly)**: top de productos (pastel), producción por supervisor (barras) y tendencia diaria (líneas).
  - **Tabla de detalle** expandible de los registros filtrados.
- **Análisis estadístico avanzado** (en el script de exploración): `sum`, `count`, `mean`, `std`, `min`, `max` por turno, producto, operador y supervisor — para distinguir volumen de **eficiencia** y **consistencia**.
- **Caché de datos** (`@st.cache_data`) para no releer la hoja en cada interacción.
- **Manejo seguro de credenciales**: nada sensible se versiona (`.gitignore`, `config.example.py`, `st.secrets` para el despliegue).

---

## 🧱 Stack tecnológico

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3 |
| Manipulación de datos | pandas |
| Dashboard / UI | Streamlit |
| Visualización | Plotly (dashboard) · Matplotlib (script de exploración) |
| Acceso a datos | gspread + oauth2client (Service Account de Google Cloud) |
| Fuente de datos | Google Sheets API |

---

## 🏗️ Arquitectura

El proyecto está **modularizado** por responsabilidad. La aplicación principal es el dashboard; el script monolítico original se conserva como banco de pruebas y exploración.

```
┌──────────────────────┐
│   Google Sheets      │   Pestaña "ENTRADAS"
│   (fuente de datos)  │   (PRODUCTO, LOTE, CANTIDAD, TURNO, OPERADOR, SUPERVISOR...)
└──────────┬───────────┘
           │  gspread + Service Account
           ▼
┌──────────────────────┐
│       etl.py         │  Extract + Transform + Load
│  load_data()         │  · autentica con st.secrets
│  @st.cache_data      │  · limpia y tipa datos → DataFrame
└──────────┬───────────┘
           ▼
┌──────────────────────┐        ┌──────────────────────┐
│    dashboard.py      │ ─────▶ │     analysis.py       │
│  (Streamlit app)     │        │  · calculate_kpis()   │
│  · filtros UI        │ ◀───── │  · generate_*_chart() │
│  · layout y KPIs     │        │    (Plotly)           │
└──────────────────────┘        └──────────────────────┘

   (legacy / exploración)
┌──────────────────────────────────────────────┐
│            ManagerInventario.py               │
│  Script monolítico original: ETL + análisis   │
│  estadístico + gráficos Matplotlib en consola │
└──────────────────────────────────────────────┘
```

**Separación de responsabilidades:**
- `etl.py` — el "cuarto de máquinas": conexión, extracción, limpieza y carga.
- `analysis.py` — cálculo de KPIs y generación de gráficos (sin estado ni UI).
- `dashboard.py` — capa de presentación: filtros, layout y orquestación.
- `ManagerInventario.py` — versión original monolítica, conservada para pruebas.

---

## 🗃️ Modelo de datos (hoja de Google Sheets)

| Pestaña | Campos relevantes |
|---------|-------------------|
| `ENTRADAS` | TIMESTAMP, PRODUCTO, LOTE DE PRODUCCIÓN, CANTIDAD (COSTALES), TURNO, OPERADOR DE EMPAQUE, SUPERVISOR DE PRODUCCIÓN, REGISTRADO POR |
| `SALIDAS` *(roadmap)* | TIMESTAMP, PRODUCTO, LOTE DE SALIDA, CANTIDAD (COSTALES), CLIENTE, NUM. ORDEN, SUPERVISOR DE EMBARQUE, REGISTRADO POR |
| `INVENTARIO/STOCK` *(roadmap)* | PRODUCTO, LOTE, TOTAL ENTRADAS, TOTAL SALIDAS, STOCK (E−S) |

---

## 🚀 Instalación y ejecución

### Requisitos previos
- Python 3.
- Una **cuenta de servicio de Google Cloud** con un `credentials.json` que tenga acceso a la hoja de cálculo.
- La hoja de Google compartida con el correo de la cuenta de servicio.

### Local
```bash
# 1. Clonar e instalar dependencias
git clone https://github.com/OswaldOR45/Proyecto-19-Hermanos.git
cd Proyecto-19-Hermanos
pip install -r requirements.txt

# 2. Configurar credenciales y origen de datos
cp config.example.py config.py        # y editar sheet_url
# Colocar el archivo credentials.json en la raíz del proyecto

# 3a. Ejecutar el dashboard interactivo
streamlit run dashboard.py

# 3b. (Opcional) Ejecutar el análisis exploratorio con gráficos Matplotlib
python ManagerInventario.py
```

> Nota: `dashboard.py` está preparado para leer credenciales desde `st.secrets`, ideal para desplegar en **Streamlit Community Cloud** sin exponer archivos secretos.

### Despliegue (Streamlit Cloud)
Configura en los *Secrets* del proyecto la `sheet_url` y el bloque `gcp_service_account` con el contenido del JSON de la cuenta de servicio.

---

## 📁 Estructura del proyecto

```
Proyecto-19-Hermanos/
├── dashboard.py            # App Streamlit (capa de presentación)
├── etl.py                  # Extracción, transformación y carga
├── analysis.py             # KPIs y gráficos (Plotly)
├── ManagerInventario.py    # Script monolítico original (exploración)
├── config.example.py       # Plantilla de configuración
├── requirements.txt
└── .gitignore              # Excluye credentials.json, config.py, .venv, etc.
```

---

## 🛣️ Roadmap

- [ ] **Fase 2 — Salidas y embarques**: integrar la pestaña `SALIDAS`.
- [ ] **Inventario PEPS/FIFO**: cálculo de stock por lote (entradas − salidas).
- [ ] Métricas de eficiencia y consistencia integradas al dashboard (hoy viven en el script de exploración).
- [ ] Exportación de reportes.
- [ ] Pruebas unitarias para las funciones de ETL y de cálculo.

---

## 🔒 Nota de seguridad

El archivo `credentials.json` está correctamente excluido del repositorio. **Recomendación**: `config.py` aparece en `.gitignore` pero quedó versionado desde antes de ignorarlo, por lo que la URL de la hoja sigue en el historial. Conviene removerlo del control de versiones (`git rm --cached config.py`) para no exponer el origen de datos.

---

## 👤 Autor

**Oswaldo Reynoso Robles** — diseño del pipeline ETL, análisis de datos y dashboard. Proyecto desarrollado como practicante de IT para apoyar la toma de decisiones de producción en planta.
