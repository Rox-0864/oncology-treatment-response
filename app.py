"""App Streamlit para predecir la respuesta al tratamiento oncológico.

Correcciones frente a ``App_neurodx.py`` (versión original):
- La predicción usa el MISMO pipeline guardado (preprocesamiento + modelo),
  así que ya no hay desajuste de features entre entrenamiento y predicción.
- ``joblib`` ahora sí está en ``requirements.txt``.
- Se agregó un aviso médico obligatorio.

Ejecutar desde la raíz del repositorio:

    streamlit run app.py
"""

from __future__ import annotations

import os

import joblib
import pandas as pd
import streamlit as st

from config import Config

cfg = Config()

MODEL_PATH = os.path.join(cfg.model_dir, f"{cfg.model_name}_pipeline.pkl")

st.set_page_config(page_title="NeuroDx — Predicción de respuesta", layout="wide")


# ------------------------------------------------------------------ Aviso médico
st.warning(
    "⚠️ **Aviso importante:** esta herramienta es un **demo educativo y de "
    "investigación**, NO un dispositivo médico. No debe usarse para tomar "
    "decisiones clínicas. Los resultados deben ser validados por un profesional "
    "de la salud."
)

st.markdown("## 🧠 NeuroDx — Predicción de respuesta al tratamiento")
st.caption("Modelo predictivo basado en datos clínicos des-identificados.")


# ------------------------------------------------------------------ Carga del modelo
@st.cache_resource(show_spinner=False)
def load_pipeline(path: str):
    if not os.path.exists(path):
        return None
    return joblib.load(path)


pipe = load_pipeline(MODEL_PATH)

if pipe is None:
    st.error(
        f"No se encontró el modelo en `{MODEL_PATH}`.\n\n"
        "Entrenalo primero con `python main.py --model " + cfg.model_name + "`."
    )
    st.stop()


# ------------------------------------------------------------------ Opciones (categorías)
@st.cache_data(show_spinner=False)
def load_categories(data_path: str):
    if not os.path.exists(data_path):
        return {}
    df = pd.read_csv(data_path, encoding=cfg.encoding)
    cats = {}
    for col in cfg.categorical_cols:
        if col in df.columns:
            vals = sorted(str(v) for v in df[col].dropna().unique())
            cats[col] = vals
    return cats


categories = load_categories(cfg.data_path)

CLASS_LABELS = {0: "Fracaso (progresión)", 1: "Éxito (control de enfermedad)"}


def predict(df_input: pd.DataFrame) -> tuple[int, float]:
    proba = pipe.predict_proba(df_input)[0]
    pred = int(pipe.predict(df_input)[0])
    return pred, float(proba[pred])


# ------------------------------------------------------------------ Predicción manual
st.sidebar.header("Ingresá los datos del paciente")

input_values = {}
for col in cfg.categorical_cols:
    options = categories.get(col, [])
    input_values[col] = st.sidebar.selectbox(col, options if options else [""])

for col in cfg.numeric_cols:
    input_values[col] = st.sidebar.number_input(col, value=0.0, step=1.0)

if st.sidebar.button("Predecir"):
    try:
        df_input = pd.DataFrame([input_values])
        pred, proba = predict(df_input)
        label = CLASS_LABELS.get(pred, str(pred))
        st.sidebar.success(f"**Resultado:** {label}")
        st.sidebar.metric("Confianza", f"{proba * 100:.1f}%")
    except Exception as exc:  # noqa: BLE001
        st.sidebar.error(f"Error en la predicción: {exc}")


# ------------------------------------------------------------------ Predicción por CSV
st.header("Predicción por archivo CSV")
st.caption(
    "Subí un CSV con las mismas columnas del dataset "
    "(ver `data/dataset.csv` para el formato esperado)."
)
uploaded = st.file_uploader("CSV con los datos a predecir", type=["csv"])

if uploaded is not None:
    try:
        df_up = pd.read_csv(uploaded, encoding=cfg.encoding)
        missing = [c for c in cfg.categorical_cols + cfg.numeric_cols if c not in df_up.columns]
        if missing:
            st.error(f"Faltan columnas: {missing}")
        else:
            df_up = df_up[list(cfg.categorical_cols) + list(cfg.numeric_cols)]
            proba = pipe.predict_proba(df_up)
            preds = pipe.predict(df_up)
            result = df_up.copy()
            result["Predicción"] = [CLASS_LABELS.get(int(p), str(p)) for p in preds]
            result["Probabilidad"] = proba.max(axis=1).round(4)
            st.dataframe(result)

            st.download_button(
                "Descargar resultados",
                data=result.to_csv(index=False).encode("utf-8"),
                file_name="predicciones.csv",
                mime="text/csv",
            )
    except Exception as exc:  # noqa: BLE001
        st.error(f"Error al procesar el archivo: {exc}")
