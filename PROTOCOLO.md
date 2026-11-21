# Protocolo de recolección de datos — Predicción de respuesta en metástasis cerebrales tratadas con SRS

> Documento técnico para organizar la recolección de datos de una **nueva
> investigación válida**. Complementa el aprendizaje del proyecto original:
> los errores de ese proceso (endpoint ambiguo, falta de variables pronósticas,
> tamaño de muestra insuficiente y fuga de datos) se corrigen de raíz acá.

---

## 1. Pregunta de investigación (PICO)

| Componente | Definición |
|------------|------------|
| **P**oblación | Pacientes adultos con metástasis cerebrales de tumor sólido tratados con radiocirugía estereotáctica (SRS) |
| **I**ntervención | SRS (dosis única o hipofraccionada), con su técnica, dosis y fraccionamiento |
| **C**omparación | Entre grupos de exposición (dosis, técnica, subtipo molecular, tratamiento sistémico concurrente) |
| **O**utcome | **Tiempo a la progresión** (endpoint primario) y supervivencia global (secundario) |

**Pregunta concreta:** *¿Qué factores clínicos, del tumor y del tratamiento
predicen el tiempo a la progresión en pacientes con metástasis cerebrales
tratadas con SRS?*

---

## 2. Endpoints (definidos ANTES de recolectar)

- **Primario**: Tiempo a la progresión (TTP) — días desde la fecha de SRS hasta la
  progresión (según criterios **RANO-BM**), censurado a la última visita.
- **Secundarios**:
  - Supervivencia global (OS) — hasta muerte o última visita.
  - Progresión sí/no a 12 meses (para clasificación binaria auxiliar).
  - Radionecrosis (efecto adverso relevante).

> **Lección del proyecto anterior**: el endpoint binario "éxito/fracaso" era
> ambiguo (¿ESTABLE es éxito o fracaso?). El endpoint **temporal** elimina esa
> ambigüedad y usa más información.

---

## 3. Diseño del estudio

- **Tipo**: cohorte observacional, preferentemente **retrospectiva con
  formulario estandarizado** (más rápida) o **prospectiva** (más robusta).
- **Tiempo cero**: fecha de la SRS. Todas las variables se miden antes o en el
  momento de la SRS (nada de información futura).
- **Seguimiento**: mínimo 12 meses por paciente, idealmente 24.

### Criterios de inclusión

- Edad ≥ 18 años.
- Metástasis cerebrales de tumor sólido, confirmadas por imagen.
- Tratadas con SRS (dosis única o hipofraccionada).
- Seguimiento con resonancia magnética (RM) disponible.

### Criterios de exclusión

- SRS previa en la misma lesión.
- Radioterapia holocraneal (whole-brain) concurrente.
- Enfermedad leptomeníngea.
- Seguimiento < 6 meses sin evento.

---

## 4. Cálculo de tamaño de muestra

Regla **EPV (eventos por variable)**: se necesitan **10–20 eventos** (progresiones)
por cada variable predictora en el modelo.

- Variables predictoras previstas: **~12**.
- **Mínimo conservador**: 12 × 10 = **120 eventos de progresión**.
- **Recomendado**: 12 × 20 = **240 eventos**.
- Considerando censura/pérdidas (~20–30%): reclutar datos para **300+ eventos**.

**Comparación con lo actual**: el proyecto original tenía **12–16 progresiones**.
Se necesita **~10–25 veces más**.

> Para estimar un AUC con intervalo de confianza estrecho (no "0.76 con std 0.15"),
> se necesitan al menos **100–150 eventos**; idealmente 200+.

---

## 5. Diccionario de datos

Cada variable se registra con **nombre exacto, tipo, unidades y valores
permitidos**. Nada de "MULTIPLES", "Unknown" sueltos o espacios en los nombres.

### 5.1 Identificación y gobernanza

| Variable | Tipo | Valores | Obligatoria | Notas |
|----------|------|---------|-------------|-------|
| `ID_PACIENTE` | texto | hash pseudoanonimizado | Sí | NUNCA nombre ni número de expediente |
| `ID_LESION` | texto | hash o secuencial por lesión | Sí | para anidar lesiones en paciente |

### 5.2 Demográficos

| Variable | Tipo | Unidades/Valores | Obligatoria |
|----------|------|------------------|-------------|
| `EDAD` | numérico | años (entero) | Sí |
| `SEXO` | categórico | M / F | Sí |

### 5.3 Estado clínico (faltantes en el proyecto anterior, claves)

| Variable | Tipo | Valores | Obligatoria |
|----------|------|---------|-------------|
| `KPS` | numérico | 0–100 (Karnofsky) | **Sí** (predictor #1) |
| `GPA` | numérico | 0–4 (Graded Prognostic Assessment) | Sí |
| `ENFERMEDAD_EXTRACRANEAL` | categórico | ausente / controlada / activa | Sí |
| `SINTOMAS_NEUROLOGICOS` | binario | 0/1 | Sí |
| `ESTEROIDES` | binario | 0/1 | Sí |

### 5.4 Tumor primario

| Variable | Tipo | Valores | Obligatoria |
|----------|------|---------|-------------|
| `TUMOR_PRIMARIO` | categórico | mama, pulmón, melanoma, renal, colorrectal, otro | Sí |
| `SUBTIPO_HISTOLOGICO` | categórico | texto libre estandarizado | Sí |
| `PERFIL_MOLECULAR` | categórico | HER2, EGFR, ALK, BRAF, triple negativo, etc. | Sí |
| `INTERVALO_PRIMARIO_METS` | numérico | meses desde diagnóstico primario | Recomendado |

### 5.5 Metástasis (por lesión)

| Variable | Tipo | Valores | Obligatoria |
|----------|------|---------|-------------|
| `NUMERO_METS` | numérico | entero ≥ 1 | Sí |
| `LOCALIZACION` | categórico | frontal, parietal, cerebelo, etc. (vocabulario cerrado) | Sí |
| `VOLUMEN_LESION` | numérico | cm³ (o mm como respaldo) | Sí |
| `EDEMA` | binario | 0/1 | Recomendado |

### 5.6 Tratamiento

| Variable | Tipo | Valores | Obligatoria |
|----------|------|---------|-------------|
| `SRS_TECNICA` | categórico | VMAT, Gamma Knife, CyberKnife, LINAC | Sí |
| `SRS_DOSIS` | numérico | Gy | Sí |
| `SRS_FRACCIONAMIENTO` | categórico | dosis única / hipofraccionado | Sí |
| `FECHA_SRS` | fecha | AAAA-MM-DD | Sí (tiempo cero) |
| `CIRUGIA_PREVIA` | binario | 0/1 | Sí |
| `RT_PREVIA` | binario | whole-brain previa 0/1 | Sí |
| `TRATAMIENTO_SISTEMICO` | categórico | QT, IT, TT, HT, combinado, ninguno | Sí |

### 5.7 Seguimiento (para supervivencia)

| Variable | Tipo | Valores | Obligatoria |
|----------|------|---------|-------------|
| `FECHA_SEGUIMIENTO_*` | fecha | una por visita | Sí |
| `FECHA_PROGRESION` | fecha | AAAA-MM-DD (o vacío si no) | Sí |
| `FECHA_MUERTE` | fecha | AAAA-MM-DD (o vacío) | Sí |
| `FECHA_ULTIMA_VISITA` | fecha | para censura | Sí |
| `RADIONECROSIS` | binario | 0/1 | Sí |

### 5.8 Outcome derivado (se calcula, no se recolecta)

| Variable | Fórmula |
|----------|---------|
| `TTP_DIAS` | `FECHA_PROGRESION - FECHA_SRS` (o censura a última visita) |
| `EVENTO_PROGRESION` | 1 si progresó, 0 si censurado |
| `OS_DIAS` | `FECHA_MUERTE - FECHA_SRS` (o censura) |

---

## 6. Formato de recolección

- **Una fila por LESIÓN**, con `ID_PACIENTE` para anidar (una fila por paciente
  se obtiene por agregación: el paciente **fracasa si cualquier lesión progresa**).
- **Formulario cerrado** (menús desplegables, no texto libre) para variables
  categóricas. Esto evita "MULTIPLES", "Unknown" y sinónimos.
- **Fechas en formato ISO** (AAAA-MM-DD), siempre en columnas separadas.
- **Validación de rango** al cargar (KPS 0–100, dosis > 0, edad 18–120).

---

## 7. Anonimización y ética

- **Aprobación del comité de ética (IRB)** antes de recolectar.
- **Anonimización en el origen**: el formulario nunca captura nombre ni expediente;
  usa un `ID_PACIENTE` hasheado (como `src/data/deidentify.py`).
- **Consentimiento informado** si es prospectivo.
- **Almacenamiento seguro** y acceso restringido.

---

## 8. Metodología de análisis (aprendido del proyecto)

1. **Validación con `GroupKFold` por `ID_PACIENTE`** (nunca split por fila).
2. **Análisis principal de supervivencia**: Cox proportional hazards o Random
   Survival Forest (usa `TTP_DIAS` y censura).
3. **Clasificación binaria** (progresión a 12 meses) como análisis secundario,
   con AUC-ROC y reporte de clasificación (no exactitud).
4. **Explicabilidad**: SHAP sobre el modelo final para que el clínico entienda
   *por qué*.
5. **Validación externa** si es posible: una cohorte temporal u hospitalaria
   separada como prueba final.

---

## 9. Checklist de arranque

- [ ] Pregunta PICO y endpoint primario escritos y aprobados.
- [ ] Cálculo de tamaño de muestra (EPV) documentado.
- [ ] Diccionario de datos versionado (este documento).
- [ ] Formulario de recolección cerrado y validado.
- [ ] Aprobación ética (IRB) y plan de anonimización.
- [ ] Plan de análisis pre-registrado (endpoints, validación GroupKFold, supervivencia).
