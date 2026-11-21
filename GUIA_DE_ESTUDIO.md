# Guía de estudio — errores encontrados y cómo se corrigieron

Esta guía documenta los problemas reales encontrados en el proyecto original
(`s20-10-data`, marca *Neuro-TX-Latam* / *NeuroDx*): dos descargas con 5
notebooks, una app Streamlit y el dataset clínico. Cada sección sigue el
formato **problema → por qué es un error → corrección**.

---

## 1. Privacidad — el número de historia clínica en los datos

### El problema
`dataset.csv` (466 filas) y `NoContry.xlsx` contenían la columna **`EXPEDIENTE`**
(el número de historia clínica, p. ej. `209406`) en texto plano.

### Por qué es un error
El número de historia clínica es un **identificador directo**: permite
re-identificar al paciente. Publicarlo en un repositorio abierto viola la
privacidad y, en muchos países, la ley de protección de datos de salud.

> Nota positiva: `NOMBRE` ya había sido eliminado y `ID_unico` ya estaba
> hasheado. El único identificador directo restante era `EXPEDIENTE`.

### La corrección
- Se creó `src/data/deidentify.py`: reemplaza `EXPEDIENTE` por un `PACIENTE`
  pseudoanonimizado (hash SHA-256 con *salt* privada), conservando la
  agrupación por paciente.
- Se eliminó `ID_unico` (identificador por fila, innecesario).
- El archivo crudo va a `data/raw/` (ignorado por git); solo se versiona la
  versión des-identificada.
- `scripts/check_data.py` verifica que no haya PII antes de commitear.

```python
# Antes
df['EXPEDIENTE']          # 209406, 225523, ...

# Después
df['PACIENTE']            # PT-3f9a2c81ab, PT-...
```

---

## 2. Dependencia faltante — `joblib` sin instalar

### El problema
`App_neurodx.py` hacía `import joblib` (línea 4) y `joblib.dump(...)` /
`joblib.load(...)`, pero `joblib` **no estaba en `requirements.txt`**.

### Por qué es un error
Al desplegar la app en Streamlit Cloud, el `pip install -r requirements.txt`
no instala `joblib`, así que la app crashea en el primer import.

### La corrección
`requirements.txt` ahora incluye `joblib==1.4.2` junto a las demás dependencias
reales (`statsmodels`, `scipy`, `xgboost`, `openpyxl`...).

---

## 3. Bug de correctitud — desajuste de encoding entre entrenamiento y predicción

### El problema
La app entrenaba sobre `dftrain.csv`, que estaba codificado con **label
encoding** (cada categoría → un número), pero la predicción usaba
`pd.get_dummies(...)` (**one-hot encoding**):

```python
# Antes: la predicción re-codificaba de forma distinta al entrenamiento
predict_data = pd.get_dummies(predict_data, drop_first=True)
```

### Por qué es un error
El modelo aprendió sobre features label-encoded, pero en predicción se le pasan
features one-hot encoded. Aunque no crashea (se reindexan columnas), **las
predicciones son incorrectas**. Es el mismo tipo de bug *silencioso* que vimos
en el proyecto de tumor cerebral.

### La corrección
Se usa un único **`Pipeline` de scikit-learn** que hace TODO el preprocesamiento
(imputación + one-hot + escalado + SMOTE) + el modelo, y se guarda **entero**
con `joblib`:

```python
pipe = build_pipeline(...)      # entrenamiento
joblib.dump(pipe, "models/random_forest_pipeline.pkl")

# En la app:
pipe = joblib.load("models/random_forest_pipeline.pkl")
pipe.predict(df_input)          # la codificación SIEMPRE coincide
```

Ya no es posible desacoplar la codificación: vive dentro del pipeline.

---

## 4. Ética — falta de aviso médico

### El problema
La app predecía la respuesta al tratamiento oncológico sin ninguna advertencia
de que no es un dispositivo médico.

### La corrección
Se agregó un aviso permanente al inicio de la app:

> "⚠️ Esta herramienta es un demo educativo y de investigación, NO un
> dispositivo médico..."

---

## 5. Limpieza de datos — nombres de columna corruptos y rutas absolutas

### El problema
- `dftrain.csv`/`dfpred.csv` tenían el header `TAMAÃ\x91O_(mm)` (mojibake de
  `TAMAÑO` por doble codificación de encoding).
- La app y los notebooks tenían rutas absolutas de máquinas concretas
  (`/mnt/data/dftrain.csv`, `/home/saul/Escritorio/...`, montajes de Google Drive).

### Por qué es un error
- Los nombres corruptos rompen el acceso a la columna.
- Las rutas absolutas hacen el proyecto no portable entre máquinas.

### La corrección
- El dataset se regenera con nombres limpios (`TAMAÑO (mm)`).
- Todas las rutas son relativas al repositorio y configurables por `config.py`.

---

## 6. Notebook roto — variables nunca definidas

### El problema
En `analisisROX.ipynb`, la celda 42-43 usaba `df_encoded` y `RESPUESTA_NUM`,
que **nunca se definían** en ninguna celda anterior:

```python
# Antes
df_imputed = pd.DataFrame(imputer.fit_transform(df_encoded), ...)  # df_encoded??
X = df_imputed.drop(columns=['RESPUESTA_NUM', 'ID'])               # RESPUESTA_NUM??
```

### Por qué es un error
El notebook no corre de corrido: se corta justo en la etapa de modelado. Nadie
puede reproducir el resultado final.

### La corrección
El pipeline modular (`src/modeling/train.py`) define explícitamente las features
(`categorical_cols` + `numeric_cols` en `config.py`) y la variable objetivo
(`RESPUESTA_BINARIA`), sin depender de variables fantasma.

---

## 7. Bug de Python — concatenación implícita de strings

### El problema
En `analisisROX.ipynb`, celda 32:

```python
if value.strip().upper() in ['CEC' 'CONO' 'IMRT' 'CONOS' 'RAPID ARC','nan']:
    return 0
```

En Python, `'CEC' 'CONO'` se concatena en `'CECCONO'` (no hay coma), y
`'RAPID ARC','nan'` forma una tupla. El resultado es una lista corrupta:
`['CECCONO', 'IMRT', 'CONOS', ('RAPID ARC','nan')]`, así que el mapeo de
`TECNICA_BIN` quedaba mal.

### Por qué es un error
Es un error de sintaxis que no da excepción: el `in` casi nunca matchea, así
que casi todo se mapea a `1`. Resultado silenciosamente incorrecto.

### La corrección
En el pipeline no hay mapeos "a mano" de este tipo: las variables categóricas
se codifican con `OneHotEncoder` dentro del `ColumnTransformer`.

---

## 8. Inconsistencia de la variable objetivo

### El problema
El notebook `analisisROX.ipynb` mapeaba `ESTABLE` → 0 (fracaso), pero el dataset
final (`dataset.csv`) trata `ESTABLE` → 1 (éxito). Dos definiciones distintas de
"éxito" en el mismo proyecto.

### Por qué es un error
Si entrenás con una definición y evaluás con otra, las conclusiones no son
coherentes.

### La corrección
Se usa una única definición, clínicamente más sensata y consistente con el
dataset final:

```python
SUCCESS_VALUES = {"RESPUESTA COMPLETA", "RESPUESTA PARCIAL", "ESTABLE"}
FAILURE_VALUES = {"PROGRESION", "PROGRESIÓN"}
```

Es decir: **éxito = control de la enfermedad (sin progresión)**; **fracaso =
progresión**. Está documentado y testeado en `tests/test_cleaning.py`.

---

## 9. Duplicación — 5 notebooks con el mismo análisis

### El problema
Entre las dos descargas había 5 notebooks (`analisisROX`, `Copia_de_Análisis_METS_OPS`,
`analisis&modelos`, `analisisAgrupXPac`, `Angel`) que repetían los mismos tests
(chi-cuadrado sobre SRS, Random Forest, etc.).

### Por qué es un error
Mantener la misma lógica en 5 lugares hace imposible saber cuál es la versión
correcta.

### La corrección
Se consolidó todo en un único pipeline modular: `src/analysis/stats.py` para los
tests y `src/modeling/train.py` para los modelos.

---

## 10. Desbalance extremo de clases

### El problema
La variable objetivo está fuertemente desbalanceada: **450 éxitos vs 16
fracasos** (~3% de la clase minoritaria).

### Por qué es un error
Con ese desbalance, la **exactitud es engañosa**: un modelo que siempre predice
"éxito" alcanza ~96% de exactitud sin aprender nada.

### La corrección
- Se usa **SMOTE** para balancear el conjunto de entrenamiento (configurable
  con `--no-smote`).
- Se evalúa con **AUC-ROC** como métrica principal y con el reporte de
  clasificación (precision/recall/F1) de la clase minoritaria.
- Se documenta la limitación: con 16 casos positivos, los resultados son
  ruidosos y NO tienen validez clínica.

---

## 11. `requirements.txt` incompleto

### El problema
El `requirements.txt` original listaba 7 paquetes, pero el código usaba
`joblib`, `statsmodels`, `scipy`, `xgboost` y `openpyxl`, ninguno de ellos
declarado.

### La corrección
Se reescribió `requirements.txt` con **todas** las dependencias reales y
versionadas.

---

## 12. Valores no numéricos en columnas numéricas (hallado al probar)

### El problema
Al ejecutar el pipeline por primera vez, el imputer numérico crasheaba con
`could not convert string to float: 'MULTIPLES'`. Inspeccionando los datos, la
columna `No. METS` contenía el string `MULTIPLES`, y `TAMAÑO (mm)` contenía
`2024-06-11 00:00:00` y `Unknown`.

### Por qué es un error
Las columnas numéricas deben ser numéricas. Un solo valor string rompe el
entrenamiento completo (el imputer no puede calcular la mediana). Es un problema
de calidad del dato de origen (un humano escribió "MULTIPLES" en lugar de un
número).

### La corrección
Se agregó `coerce_numeric()` en `src/data/cleaning.py`: convierte cada columna
numérica con `pd.to_numeric(errors="coerce")`, de modo que cualquier valor no
numérico se vuelve `NaN` y luego lo imputa el pipeline. El resultado se detectó
**porque se probó el pipeline de punta a punta**, no porque nadie lo hubiera
visto antes.

---

## 13. Fuga de datos — validar sin agrupar por paciente (el hallazgo más importante)

### El problema
El pipeline original (y el primer split que hicimos) dividía los datos por
**fila**, ignorando que los 466 tumores pertenecen a **97 pacientes**. Un mismo
paciente podía quedar con tumores en el conjunto de entrenamiento *y* en el de
prueba.

### Por qué es un error
Cuando un paciente aparece en train y test, el modelo "ya lo vio" durante el
entrenamiento. Eso **infla las métricas**: el AUC parecía 0.83, pero era fuga de
información, no capacidad real.

### La prueba
Al usar `GroupKFold` (separando por `PACIENTE`), el AUC **colapsa a ~0.48
(nivel azar)** y el recall de progresión es 0 en todos los folds:

| Split | AUC | Conclusión |
|-------|-----|-----------|
| Aleatorio (por fila) | 0.83 | falso optimismo (fuga) |
| GroupKFold (por paciente) | 0.48 | nivel azar |

### La corrección
Se agregó `src/modeling/group_eval.py` y `scripts/evaluate_grouped.py`, que
evalúan con `GroupKFold` por paciente (y opcionalmente calculan importancia
SHAP). Es la forma correcta de validar datos clínicos con múltiples registros
por paciente.

> **Regla de oro:** si los datos tienen una columna que identifica al sujeto
> (paciente, cliente, usuario), la validación SIEMPRE debe agruparse por esa
> columna.

---

## Resumen rápido

| # | Error | Corrección |
|---|-------|------------|
| 1 | `EXPEDIENTE` (historia clínica) en los datos | des-identificación + `check_data.py` |
| 2 | `joblib` sin declarar | `requirements.txt` completo |
| 3 | Encoding distinto en train vs predicción | `Pipeline` sklearn guardado entero |
| 4 | Sin aviso médico | disclaimer en la app |
| 5 | Headers corruptos y rutas absolutas | nombres limpios + rutas relativas |
| 6 | Variables fantasma (`df_encoded`) | pipeline modular explícito |
| 7 | Concatenación implícita de strings | `OneHotEncoder` (sin mapeos a mano) |
| 8 | Dos definiciones de "éxito" | mapeo único y testeado |
| 9 | 5 notebooks duplicados | un solo pipeline |
| 10 | Desbalance 450 vs 16 | SMOTE + AUC-ROC |
| 11 | `requirements.txt` incompleto | deps reales y pineadas |
| 12 | Strings en columnas numéricas (`MULTIPLES`) | `coerce_numeric()` |
| 13 | Fuga de datos por no agrupar por paciente | `GroupKFold` por `PACIENTE` |
