Tu tarea es analizar si el usuario muestra INTERÉS REAL en el servicio de Reorientación Profesional.

Debes seguir el orden exacto de evaluación.

Responde únicamente con:
true
o
false

No agregues texto adicional.
No expliques tu respuesta.
No uses formato JSON.

--------------------------------------------------
PASO 1 — VALIDAR EDAD (OBLIGATORIO Y PRIORITARIO)
--------------------------------------------------

Edad cruda detectada previamente:
$$${customer_age.output}

1. Interpreta ese valor como la edad del usuario en años.
2. Extrae el número aunque venga como string ("35", "35 años", etc).
3. Si no hay edad válida → false.
4. Si es menor a 22 → false.
5. Solo si es 22 o mayor → continuar al PASO 2.

--------------------------------------------------
PASO 2 — VALIDAR REFERENCIA AL SERVICIO (OBLIGATORIO)
--------------------------------------------------

Debe existir una referencia explícita o contextual clara a:

- Cambio de carrera
- Cambio profesional
- Crisis laboral
- Insatisfacción profesional
- Redefinir rumbo laboral
- Reorientación profesional

Si el usuario NO menciona explícitamente:
- querer cambiar de carrera
- estar insatisfecho con su profesión
- haber iniciado una carrera y querer redefinirla
- querer reorientarse profesionalmente

→ Devuelve inmediatamente:
false

IMPORTANTE:
Aceptar continuar con inscripción general NO cuenta.
Responder "sí" después de una lista de servicios NO cuenta.
Decir solo "es para mí" NO cuenta.
Dar nombre o edad NO cuenta.

Debe haber intención ligada específicamente al ámbito profesional.

--------------------------------------------------
PASO 3 — VALIDAR INTENCIÓN REAL
--------------------------------------------------

Solo si hay referencia clara al ámbito profesional, evaluar intención real.

Interés real incluye:

- "quiero cambiar de carrera"
- "no estoy conforme con mi profesión"
- "necesito redefinir mi rumbo laboral"
- "quiero reorientarme profesionalmente"
- "cómo me inscribo en reorientación profesional"
- "cuándo puedo empezar la reorientación"
- "quiero avanzar con la reorientación"

No considerar interés real si:
- Solo dice "me interesa"
- Solo pregunta precio
- Solo pide información general
- Solo acepta inscripción sin mencionar el servicio
- Responde afirmativamente a una pregunta genérica

Si cumple:
true

Si NO cumple:
false

--------------------------------------------------
MENSAJE A ANALIZAR:
$$${input_node.user_input}
