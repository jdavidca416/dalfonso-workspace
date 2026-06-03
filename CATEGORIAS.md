# Categorías del flujo

Documento de referencia sobre las **categorías de clasificación** usadas en el flujo de Lucrecia. La fuente de verdad es `PromptNodes/triggers_detection.md`; este archivo resume su propósito, su rango de valores y cómo se consumen aguas abajo.

---

## 1. Propósito

`triggers_detection` es el nodo encargado de **leer cada mensaje del usuario y decidir si dispara una escalada (handoff a un orientador humano) o un caso de contacto explícito**. La salida es un JSON con dos campos:

```
{"keywords": <null | string | string[]>, "category": <null | "categoriaN">}
```

Ese JSON luego se parsea en dos nodos de código de `CodeNodes/GetDataNodes/`:

- `category.js` → extrae el campo `category`.
- `keywords.js` → extrae el campo `keywords`.

Y se inyecta en `prompt_scalation.md` y `prompt_handoff.md` vía `$${category}` y `$${keywords}` para construir el mensaje de derivación.

---

## 2. Valores posibles de `category`

Solo hay **8 valores válidos** (más `null`). No existe `categoria8`.

| Valor          | Nombre interno                              | Cuándo se dispara |
|----------------|---------------------------------------------|-------------------|
| `null`         | Sin clasificación                           | El mensaje no cumple ninguna regla de activación, o cae en alguna excepción (modalidad/localidad, tercero no permitido, mención a "reorientación"). |
| `categoria1`   | Condición clínica declarada                 | Depresión, ansiedad, bipolaridad, TDAH, TEA, TOC, trastornos del sueño, etc. |
| `categoria2`   | Tratamiento o medicación                    | Psiquiatra, psicólogo, medicación, internación, antidepresivos, etc. |
| `categoria3`   | Ideación suicida o autolesión               | "quiero morirme", "no quiero vivir", autolesión, pensamientos suicidas. **Prioridad máxima.** |
| `categoria4`   | Expresiones coloquiales graves              | "no puede más", "está destruido", "está en crisis", etc. |
| `categoria5`   | Padre/madre hablando de su hijo/a con síntoma | Requiere: mención literal de "mi hijo"/"mi hija" + síntoma psicológico claro + síntoma afectando al hijo/a. |
| `categoria6`   | Adulto en primera persona con síntoma       | "no puedo levantarme de la cama", "lloro todo el tiempo", "tengo ataques de ansiedad". |
| `categoria7`   | Vulnerabilidad                              | Violencia, abuso, maltrato, consumo problemático. |
| `categoria9`   | Solicitud explícita de contacto             | Verbo de comunicación (contactar, llamar, escribir, agendar, sacar turno) **y/o** mención directa de canal (WhatsApp, teléfono, mail, Instagram, número). |

---

## 3. Reglas de activación (resumen)

El prompt aplica filtros en orden y devuelve `null` apenas alguno falla:

1. **Paso 0 — Excepción modalidad/localidad.** Si el mensaje solo menciona modalidad (presencial, virtual, online) o lugar (ciudad, barrio, país), `category = null`.
2. **Paso 1 — Filtro de sujeto.** Si se menciona a un tercero distinto de "mi hijo"/"mi hija" (primo, sobrino, amigo, paciente, etc.), `category = null`.
3. **Paso 2 — Detección de categoria9.** Solo si hay solicitud explícita de contacto.
4. **Paso 3 — Regla de activación obligatoria para 1–7.** Debe haber al menos uno de: síntoma psicológico explícito, diagnóstico declarado, crisis emocional, vulnerabilidad concreta, tratamiento o medicación. **No** clasifica por edad, datos demográficos, interés académico, confirmaciones, información neutral, confusión vocacional ni dudas sobre qué estudiar.
5. **Paso 4 — Prioridad entre coincidencias** (de mayor a menor):
   `categoria3` > `categoria7` > `categoria1` > `categoria2` > `categoria5` > `categoria6` > `categoria4`.
6. **Paso 5 — Keywords.** Solo para `categoria1`–`categoria7`. Mínimo 1, máximo 5. Sin edad ni términos neutros.

Excepción transversal: si el mensaje menciona "reorientación" o "reorientación profesional", devuelve `{"keywords": null, "category": null}` (el servicio REO ya no se ofrece).

---

## 4. Formato de salida obligatorio

| Caso                       | Salida JSON exacta                                        |
|----------------------------|-----------------------------------------------------------|
| Sin clasificación          | `{"keywords": null, "category": null}`                    |
| Categorías 1–7             | `{"keywords": ["keyword1", "keyword2"], "category": "categoriaN"}` |
| Categoría 9                | `{"keywords": null, "category": "categoria9"}`            |

Reglas duras:
- El campo `keywords` nunca se omite.
- Para categorías 1–7, `keywords` es obligatorio (no `null`).
- Para `categoria9`, `keywords` **debe** ser `null`.
- La salida es JSON crudo, sin comillas envolventes, sin prefijo `json`, sin explicaciones.

---

## 5. Cómo se consumen las categorías aguas abajo

`prompt_scalation.md` arma el bloque de evaluación:

```
🚨 Handoff category evaluation
handoff_category: $${category}
detected_keywords: $${keywords}
```

`prompt_handoff.md` decide a quién dirigirse (interesado vs tutor) y produce el mensaje de derivación canónico:

> "[nombre] para comprender mejor tu inquietud, vamos a derivarte a uno de nuestros orientadores. En las próximas 24hs hábiles se van a estar contactando con vos."

El estilo del mensaje de handoff prohíbe: empatía previa, mayúsculas enfáticas, números de emergencia, y la frase "nuestro equipo de especialistas".

---

## 6. Otras categorizaciones del flujo (no confundir)

Para evitar ambigüedad con la palabra "categoría", el flujo tiene tres clasificaciones distintas:

- **`prompt_orchestrator.md` — Intents de ruteo.** Clasifica cada turno en `recommend`, `schedule` u `other`. Decide qué prompt responde, no si se escala. Independiente de `triggers_detection`.
- **`triggers_detection.md` — Categorías clínicas/contacto.** Lo descrito en este documento. Decide escalada humana.
- **`no_study_detection.md` — Bandera de escalada por trayectoria académica.** Salida booleana (`true`/`false`). Se dispara solo si edad ≥ 22 y el usuario declara ausencia total de estudios o múltiples intentos fallidos. Al activarse, `no_study_scalation.md` genera un mensaje de derivación específico ("escalamiento por No Estudios").

Las tres pueden coexistir en una misma conversación, pero cada una corre en su propio nodo y produce salidas independientes.

---

## 7. Pendientes / notas operativas

- Mantener la numeración de categorías estable (existe gap intencional entre 7 y 9). Si se agrega una nueva, evaluar si requiere ajuste en la tabla de prioridad del Paso 4.
- La excepción de "reorientación" debe mantenerse mientras REO esté fuera de oferta. Si REO vuelve, esa regla debe revisarse.
