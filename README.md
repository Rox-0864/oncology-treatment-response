# Oncology Treatment Response — NeuroDx 🧠

Análisis estadístico y predictivo de la **respuesta al tratamiento** en pacientes
oncológicos con metástasis cerebrales tratadas con **radiocirugía estereotáctica
(SRS)**, evaluada con los **criterios RANO**.

> ⚠️ **Aviso:** este proyecto es un trabajo educativo y de investigación. **NO es
> un dispositivo médico** y no debe usarse para decisiones clínicas.

Este repositorio consolida y corrige el proyecto original del equipo
(`s20-10-data`, marca *Neuro-TX-Latam* / *NeuroDx*). Los errores corregidos y su
explicación están documentados en la **[guía de estudio](GUIA_DE_ESTUDIO.md)**.

---

## 🔒 Privacidad de los datos

El dataset original contenía el **número de historia clínica** (`EXPEDIENTE`),
un identificador directo que **no debe publicarse**.

En este repositorio los datos están **des-identificados**:

- `EXPEDIENTE` fue reemplazado por un `PACIENTE` pseudoanonimizado (hash SHA-256
  con *salt* privada, ver `src/data/deidentify.py`).
- `NOMBRE` e `ID_unico` fueron eliminados.
- El archivo crudo **NO se versiona** (va en `data/raw/`, ignorado por git).

**Nunca comitees el Excel/CSV crudo con `EXPEDIENTE`.** Para preparar datos
nuevos usá `scripts/deidentify.py`.

---

## Estructura del proyecto

```
oncology-treatment-response/
├── config.py                 # toda la configuración (columnas, modelo, rutas)
├── main.py                   # pipeline: limpiar + analizar + entrenar
├── app.py                    # app Streamlit de predicción
├── data/
│   └── dataset.csv           # dataset DES-IDENTIFICADO (466 registros)
├── src/
│   ├── data/
│   │   ├── loader.py         # carga CSV/Excel
│   │   ├── deidentify.py     # pseudoanonimización
│   │   └── cleaning.py       # normalización y limpieza
│   ├── analysis/
│   │   └── stats.py          # chi2, ANOVA, Fisher, test Z
│   ├── modeling/
│   │   └── train.py          # pipeline sklearn + SMOTE + evaluación
│   └── utils/
│       ├── logging.py
│       └── plotting.py
├── scripts/
│   ├── deidentify.py         # prepara un dataset crudo para publicar
│   └── check_data.py         # verifica que no haya PII
├── tests/
│   ├── test_deidentify.py
│   └── test_cleaning.py
└── requirements.txt
```

---

## Requisitos e instalación

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate          # Windows

pip install -r requirements.txt
```

## Uso

### 1. Verificar los datos

```bash
python scripts/check_data.py
```

### 2. Entrenar el modelo

```bash
python main.py                     # Random Forest (default)
python main.py --model xgboost    # otro modelo
python main.py --stats            # incluye pruebas estadísticas
python main.py --help
```

Esto limpia los datos, entrena con el pipeline (imputación + one-hot + SMOTE +
modelo) y guarda en `results/`: métricas (`metrics.json`), reporte de
clasificación, matriz de confusión, curva ROC e importancia de features. El
pipeline completo queda en `models/`.

### 3. Ejecutar la app

```bash
streamlit run app.py
```

---

## Modelos disponibles

| Nombre | Descripción |
|--------|-------------|
| `random_forest` | Bosque aleatorio (default) |
| `gradient_boosting` | Gradient Boosting |
| `logistic` | Regresión logística |
| `decision_tree` | Árbol de decisión |
| `xgboost` | XGBoost |

**Métrica principal: AUC-ROC.** La clase minoritaria (progresión) representa
~3% de los datos (16 de 466), por lo que la exactitud es engañosa: un modelo
que siempre predice "éxito" tendría ~96% de exactitud. Por eso se usa SMOTE y
se evalúa con AUC-ROC y las métricas de la clase minoritaria.

---

## Sobre los datos

- **Fuente:** datos clínicos del proyecto No-Country `s20-10-data`, aportados
  por una médica (metástasis cerebrales tratadas con SRS).
- **Registros:** 466 tumores de 97 pacientes (varios tumores por paciente).
- **Variables:** edad, sexo, tumor primario, subtipo histológico, perfil
  molecular, localización, tamaño, dosis, técnica, tratamiento sistémico,
  cirugía previa, SRS y respuesta (RANO → binaria).
- **Clases:** éxito (control de enfermedad) = 450 · fracaso (progresión) = 16.

> **Limitación importante:** el desbalance extremo y el tamaño pequeño de la
> clase minoritaria hacen que los resultados sean ruidosos. Es un proyecto de
> aprendizaje, no un modelo con validez clínica.

---

## Guía de estudio

Los errores del proyecto original y cómo se corrigieron están explicados en
**[GUIA_DE_ESTUDIO.md](GUIA_DE_ESTUDIO.md)**.
