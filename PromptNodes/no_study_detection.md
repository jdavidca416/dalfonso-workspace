Tu tarea es analizar lo siguiente:

Debes seguir estrictamente el orden indicado.
No puedes omitir pasos.
No puedes asumir información faltante.

Responde únicamente con:
true
o
false

No agregues texto adicional.
No expliques tu respuesta.
No uses formato JSON.

--------------------------------------------------
PASO 1 — CONFIRMAR QUE LA EDAD FUE EXPLÍCITAMENTE PROPORCIONADA
--------------------------------------------------

Edad cruda detectada previamente:
current_age = $$${cage}

REGLA PRIORITARIA: Si current_age es un número menor a 22, devuelve INMEDIATAMENTE false. NO continúes al siguiente paso. Esta regla tiene MÁXIMA PRIORIDAD y se aplica ANTES de cualquier otra evaluación.

Reglas estrictas:

1. La edad debe haber sido mencionada explícitamente por el usuario en la conversación.
2. La variable debe contener un valor real.
3. No puedes inferir edad por contexto.
4. No puedes asumir edad aproximada.
5. Si la variable:
   - No existe
   - Está vacía
   - Es null
   - Es undefined
   - Es una cadena vacía
   - Contiene texto sin número identificable

→ Devuelve inmediatamente:
false

NO continúes al PASO 2.

--------------------------------------------------
PASO 2 — EXTRAER Y VALIDAR EDAD
--------------------------------------------------

1. Extrae un número claro que represente edad en años.
   Puede venir como:
   "25"
   "25 años"
   "Tengo 30"
   "30 años"

2. Si no puedes identificar un número explícito:
   → false

3. Si current_age es menor a 22:
   → false

4. Solo si current_age es 22 o mayor:
   → Continúa al PASO 3.

--------------------------------------------------
PASO 3 — EVALUAR PERFIL ACADÉMICO
--------------------------------------------------

Devuelve true SOLO si el mensaje contiene explícitamente:

A) Ausencia total de estudios
   - "no estudié nada"
   - "nunca estudié"
   - "no tengo estudios"
   - "no hice ninguna carrera"
   - "nunca hice estudios superiores"

O

B) Múltiples cambios o intentos fallidos
   - "cambié varias veces de carrera"
   - "empecé varias carreras y no terminé ninguna"
   - "he dejado varias carreras"
   - "probé muchas cosas y no terminé nada"
   - "ya intenté varias opciones y no funcionó"

Condiciones adicionales estrictas:

- Debe referirse a sí mismo.
- No debe hablar de otra persona.
- No debe ser una hipótesis.
- No debe ser pregunta general.
- No debe ser solo interés en reorientación.
- No debe ser ambigüedad.

Si cumple todo:
true

Si NO cumple:
false

--------------------------------------------------
MENSAJE A ANALIZAR:
$$${input_node.user_input}
