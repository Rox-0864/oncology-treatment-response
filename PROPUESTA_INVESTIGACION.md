# Propuesta de investigación — Predicción de respuesta al tratamiento en metástasis cerebrales tratadas con SRS

> **Documento formal para presentar al equipo médico.** Busca convencer sobre la
> recolección de datos para construir un modelo predictivo clínicamente útil y
> metodológicamente válido.

---

## Título

**"Modelo predictivo del tiempo a la progresión en pacientes con metástasis
cerebrales tratadas con radiocirugía estereotáctica (SRS): un estudio de cohorte
con aprendizaje automático"**

---

## Resumen ejecutivo

Las metástasis cerebrales son una complicación frecuente y determinante del
cáncer avanzado. La radiocirugía estereotáctica (SRS) es un tratamiento eficaz,
pero **no todos los pacientes responden igual**: algunos progresan rápido y
otros mantienen control por largo tiempo.

Proponemos construir un **modelo predictivo** que, a partir de datos clínicos
rutinarios del paciente y su tumor, estime **qué pacientes tienen mayor riesgo
de progresión** y en qué plazo. Esto permitiría **personalizar el seguimiento**
(frecuencia de RM) y **anticipar decisiones terapéuticas**.

Contamos con un análisis preliminar sobre un conjunto de 466 registros que
identificó una **señal predictiva prometedora (AUC ~0.72–0.76)**, pero también
evidenció que el tamaño de muestra actual (12–16 casos de progresión) es
insuficiente para un modelo clínicamente válido. **Para dar el siguiente paso
necesitamos ampliar la recolección de datos**, que es exactamente lo que
solicitamos a su equipo.

---

## Planteamiento del problema

- Las metástasis cerebrales ocurren en ~10–30% de los pacientes oncológicos.
- La SRS logra altas tasas de control local, pero la **progresión** sigue siendo
  frecuente y su predicción es clínica y subjetiva.
- Los scores pronósticos actuales (GPA, DS-GPA) dan una estimación gruesa, pero
  **no incorporan la riqueza de datos individuales** que hoy se registran de
  rutina.
- Existe la oportunidad de aplicar **aprendizaje automático** para un modelo más
  preciso y **explicable**, que apoye (no reemplace) el juicio clínico.

---

## Objetivos

### Objetivo general

Desarrollar y validar un modelo predictivo del **tiempo a la progresión** en
pacientes con metástasis cerebrales tratadas con SRS, basado en variables
clínicas, del tumor y del tratamiento.

### Objetivos específicos

1. Identificar los **factores pronósticos** asociados a la progresión (incluido
   KPS, GPA, enfermedad extracraneal y características del tratamiento).
2. Construir un modelo de **supervivencia** (Cox / Random Survival Forest) y uno
   de **clasificación** (progresión a 12 meses).
3. Cuantificar el rendimiento con **validación rigurosa** (agrupada por paciente)
   y **explicabilidad** (SHAP) para confianza clínica.
4. Proponer una **herramienta de apoyo** para personalizar el seguimiento.

---

## Metodología (resumen)

| Aspecto | Decisión |
|---------|----------|
| Diseño | Cohorte observacional (retrospectiva con formulario estandarizado, o prospectiva) |
| Población | Adultos con metástasis cerebrales de tumor sólido tratadas con SRS |
| Endpoint primario | Tiempo a la progresión (RANO-BM), censurado |
| Variables | Demográficas, KPS, GPA, enfermedad extracraneal, tumor primario, perfil molecular, número/tamaño/localización de lesiones, dosis/técnica de SRS, tratamiento sistémico, fechas de seguimiento |
| Tamaño de muestra | **120–240 eventos de progresión** (regla 10–20 eventos por variable) |
| Validación | `GroupKFold` por paciente (evita fuga de datos) + validación externa si es posible |
| Análisis | Supervivencia (Cox / RSF) como principal; clasificación + AUC-ROC como secundario |

> El detalle técnico completo está en **[PROTOCOLO.md](PROTOCOLO.md)**.

---

## Qué necesitamos de su equipo

Concretamente, solicitamos colaboración para **recolectar datos** de la siguiente
manera:

1. **Acceso a registros** (con anonimización y aprobación ética): historiales de
   pacientes con metástasis cerebrales tratadas con SRS en los últimos 3–5 años.
2. **Completar el diccionario de datos** (variables listadas en el protocolo),
   en particular: **KPS, GPA, estado de enfermedad extracraneal, fechas de
   seguimiento y progresión**.
3. **Un formulario cerrado** para capturar los datos de forma estandarizada
   (sin texto libre) — nosotros lo preparamos y lo validamos.
4. **Tiempo clínico** para revisar y completar los registros (o designar a un
   residente/estudiante que lo haga bajo supervisión).

**Lo que NO pedimos**: datos identificables (nombres ni números de expediente).
Todo se anonimiza en el origen con un identificador hasheado.

---

## Beneficios para el equipo médico

- **Publicación científica**: un estudio con metodología sólida y resultados
  honestos es publicable y agrega valor académico al servicio.
- **Herramienta de apoyo clínico**: un modelo que ayude a decidir la frecuencia
  de seguimiento (p. ej., RM a 3 vs 6 meses según riesgo).
- **Conocimiento propio del servicio**: entender qué factores predicen la
  progresión en *su* población específica, no en cohortes ajenas.
- **Base para estudios futuros**: el diccionario y la base estandarizada quedan
  como activo reutilizable para otras preguntas (radionecrosis, toxicidad).
- **Colaboración interdisciplinaria**: equipo de datos + equipo clínico, con
  roles claros.

---

## Cronograma propuesto (6–9 meses)

| Fase | Duración | Entregable |
|------|----------|------------|
| 1. Protocolo y aprobación ética | Mes 1–2 | Protocolo aprobado (IRB) |
| 2. Formulario y diccionario | Mes 2 | Formulario de captura validado |
| 3. Recolección de datos | Mes 3–6 | Base de datos completa y anonimizada |
| 4. Limpieza y análisis | Mes 6–7 | Modelos entrenados y validados |
| 5. Informe y publicación | Mes 8–9 | Manuscrito + herramienta |

---

## Consideraciones éticas

- Aprobación del **comité de ética** antes de recolectar.
- **Anonimización** en el origen (sin nombre ni expediente; identificador
  hasheado).
- **Consentimiento informado** si la recolección es prospectiva.
- **No es un dispositivo médico**: el modelo es de investigación y apoyo, no
  sustituye el juicio clínico.

---

## Resultados esperados e impacto

- Un **modelo validado** que estime el riesgo de progresión por paciente.
- Una **lista de factores pronósticos** con su importancia (explicable con SHAP).
- Una **herramienta de apoyo** (prototipo) para personalizar el seguimiento.
- Una **publicación** que documente tanto el modelo como la metodología (incluidas
  las lecciones de validación).

> **Honestidad metodológica**: este proyecto prioriza la validez por encima del
> "resultado llamativo". Ya documentamos en nuestro análisis preliminar cómo una
> validación incorrecta produce un AUC falso de 0.83 que colapsa a 0.48 al
> corregirla. Esa transparencia es nuestra garantía de credibilidad.

---

## Equipo

| Rol | Responsabilidad |
|-----|-----------------|
| Investigador/a de datos | Diseño, análisis, modelos, documentación |
| Médico/a clínico/a | Criterios clínicos, acceso a registros, revisión de casos |
| Estadístico/a (opcional) | Revisión del diseño y análisis de supervivencia |
| Comité de ética | Aprobación y supervisión |

---

*Documento preparado para discusión con el equipo médico. Ajustable según los
recursos y prioridades del servicio.*
