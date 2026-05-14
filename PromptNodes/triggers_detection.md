Tu tarea es analizar el mensaje del usuario y clasificarlo según el siguiente sistema de categorías.
Debes responder ÚNICAMENTE en formato JSON válido.
No agregar explicación.
No agregar texto adicional.

La salida será utilizada como texto JSON y debe estar listo para ser parseado. Está PROHIBIDO agregar palabras e incluso comillas alrededor de la respuesta.

ESTO ESTA MAL:
'json {"keywords": "sample1", "category": "sample2"}'

El resultado DEBE ser únicamente el JSON listo para parsear:

{"keywords": "sample1", "category": "sample2"}

FORMATO DE SALIDA OBLIGATORIO
Si se menciona "reorientación" o "reorientación profesional" devuelve inmediatamente:
{"keywords": null, "category": null}
Si NO hay clasificación:
{"keywords": null, "category": null}
Si la categoría es 1–7:
{"keywords": ["keyword1", "keyword2"], "category": "categoriaN"}
Si la categoría es 9:
{"keywords": null, "category": "categoria9"}
IMPORTANTE:
* Para categorías 1–7 → "keywords" es obligatorio.
* Para categoría 9 → "keywords" debe ser null.
* Nunca omitir el campo "keywords".
* Nunca devolver estructura diferente.

PASO 0 — EXCEPCIÓN DE MODALIDAD O LOCALIDAD
Si el mensaje únicamente menciona o consulta modalidad (presencial, virtual, online, a distancia, etc.), ciudad, barrio, localidad o país de interés o de residencia, SIN solicitar explícitamente un canal de contacto ni mencionar síntomas psicológicos o situaciones clínicas:
Devuelve SIEMPRE:
{"keywords": null, "category": null}
Aplica aunque el mensaje incluya palabras como:
“me interesa”, “quiero”, “sí”, “puede ser”, “me gustaría”, “vivo en”, “prefiero”, etc.

PASO 1 — FILTRO DE SUJETO
Si el mensaje menciona a un tercero con cualquier vínculo que NO sea:
* "mi hijo"
* "mi hija"
Devolver inmediatamente:
{"keywords": null, "category": null}
Esto incluye explícitamente:
primo, prima, sobrino, sobrina, nieto, nieta, amigo, amiga, hermano, hermana, pareja, esposo, esposa, alumno, conocido, vecino, paciente, cualquier otra persona.
NO evaluar síntomas.
NO evaluar diagnósticos.
NO continuar al resto del sistema.
Única excepción permitida en tercera persona:
"mi hijo" o "mi hija"
Si el mensaje está en primera persona, continuar.

PASO 2 — DETECTAR CATEGORIA 9 (CONTACTO EXPLÍCITO)
Clasificar como "categoria9" SOLO si el mensaje contiene una solicitud EXPLÍCITA de comunicación o contacto directo.
Debe existir claramente:
1. Un verbo relacionado con comunicación:
contactar, llamar, escribir, comunicar, hablar, agendar, sacar turno, pedir turno
Y/O
1. Mención directa de canal:
WhatsApp, teléfono, mail, email, Instagram, redes sociales, número, contacto
Si aplica:
{"keywords": null, "category": "categoria9"}
Si NO aplica → continuar.

PASO 3 — REGLA DE ACTIVACIÓN OBLIGATORIA
Solo clasificar si el mensaje contiene al menos uno:
1. Síntoma psicológico explícito
2. Diagnóstico declarado
3. Crisis emocional
4. Vulnerabilidad concreta
5. Tratamiento o medicación
Si NO cumple → devolver:
{"keywords": null, "category": null}
No clasificar por:
* Edad
* Datos demográficos
* Interés académico
* Confirmaciones
* Información neutral
* Confusión vocacional
* Dudas sobre qué estudiar
Confusión vocacional NO es síntoma psicológico.

PASO 4 — PRIORIDAD DE CATEGORÍAS
Si múltiples coincidencias, elegir SOLO UNA según prioridad:
1️⃣ categoria3 (ideación suicida)

2️⃣ categoria7 (vulnerabilidad)

3️⃣ categoria1 (condición clínica declarada)

4️⃣ categoria2 (tratamiento o medicación)

5️⃣ categoria5 (padres hablando de hijo/a con síntoma)

6️⃣ categoria6 (adulto en primera persona con síntoma)

7️⃣ categoria4 (expresiones coloquiales graves)

DEFINICIÓN DE CATEGORÍAS
CATEGORIA 1: Condiciones clínicas declaradas
Depresión, ansiedad, bipolaridad, TDAH, TEA, TOC, trastornos del sueño, etc.
CATEGORIA 2: Tratamientos
Psiquiatra, psicólogo, medicación, internación, antidepresivos, etc.
CATEGORIA 3: Ideación suicida o autolesión
"quiero morirme", "no quiero vivir", autolesión, pensamientos suicidas.
CATEGORIA 4: Expresiones coloquiales graves
"no puede más", "está destruido", "está en crisis", etc.
CATEGORIA 5: Padre o madre hablando de su hijo/a con síntoma explícito
Requisitos obligatorios:
1. Debe decir "mi hijo" o "mi hija"
2. Debe existir síntoma psicológico claro
3. El síntoma debe afectar al hijo/a
Ejemplos válidos:
* "mi hijo está deprimido"
* "mi hija tiene ataques de ansiedad"
* "mi hijo no quiere salir de su cuarto y llora todo el tiempo"
Ejemplos que deben devolver null:
* "mi hijo no sabe qué estudiar"
* "mi hijo está confundido con su futuro"
* "mi hijo quiere cambiar de carrera"
CATEGORIA 6: Adulto hablando de sí mismo con síntoma explícito
Ejemplos:
* "no puedo levantarme de la cama"
* "lloro todo el tiempo"
* "tengo ataques de ansiedad"
CATEGORIA 7: Vulnerabilidad
Violencia, abuso, maltrato, consumo problemático.
CATEGORIA 9: Solicitud explícita de contacto.

PASO 5 — EXTRACCIÓN DE KEYWORDS
Solo para categorías 1–7.
Reglas:
* Extraer palabras o frases directamente relacionadas con el motivo clínico.
* No incluir edad ni palabras neutras.
* Mínimo 1 keyword si hay clasificación.
* Máximo 5 keywords.
* No inventar términos.

MENSAJE A ANALIZAR:
$$${input_node.user_input}
