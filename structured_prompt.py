from pydantic import BaseModel, Field
from typing import List

class StructuredPrompt1(BaseModel):
    
    # didi_cal_refusal_to_attend_or_leaving_the_chat: float = Field(
    #     ...,
    #     description="""
    #     # PERSONA
    #     Actúa como un Auditor de Calidad especializado en eficiencia operativa y retención de usuarios. Tu foco es garantizar que ninguna duda quede sin respuesta y que el agente mantenga el control del tiempo.

    #     # CONTEXTO
    #     Analizarás una interacción de chat incluyendo los tiempos de espera (timestamps) entre mensajes. Debes identificar si el agente causó la desconexión del usuario por inactividad o si el cliente simplemente no volvio a interactuar con el agente y el chat se cerro por inacividad o se evidencio una falta de voluntad de ayuda total por parte del agente.

    #     # TAREA
    #     Evaluar el mantenimiento del chat y la resolución de dudas, asignando un valor `float` según el cumplimiento de los tiempos y la actitud de servicio.

    #     # CADENA DE PENSAMIENTO (CHAIN-OF-THOUGHT)
    #     Sigue estos pasos lógicos para determinar la calificación:

    #     1. **Análisis de Resolución de Dudas:**           
    #        - ¿El agente respondió a TODAS las preguntas formuladas por el usuario?
    #        - ¿El agente declaró explícitamente que 'no ayudaría' o mostró negativa al servicio?

    #     2. **Análisis de Tiempos y Silencios (Cronometría):**
    #        - Identifica el último mensaje del usuario que requería respuesta.
    #        - Calcula el tiempo transcurrido hasta el mensaje del agente o el fin de la sesión.
    #        - **Regla Crítica:** ¿Pasaron más de **2:30 minutos** (150 segundos) de silencio por parte del agente mientras el cliente esperaba?

    #     3. **Determinación de Causa de Desconexión:**
    #        - ¿La interacción termina por inactividad del cliente osea este no volvio a interactuar con el agente?
    #        - ¿El usuario abandonó el chat porque el agente dejó de responder?

    #     4. **Asignación de Calificación (Veredicto):**
    #        - **0.0 (Cumple):** El agente respondió todo, se mantuvo activo, la interaccion termino por inactividad del cliente o cerró el chat tras una conclusión clara.
    #        - **1.0 (No Cumple):** - El agente causó el abandono por silencio (> 2:30m).
    #          - El agente dejó preguntas sin responder antes de desconectarse.
    #          - El agente se negó explícitamente a ayudar.
    #        - **2.0 (No Aplica):** La interacción se cortó por problemas técnicos ajenos al comportamiento del agente o el usuario se desconectó inmediatamenteabruptamente sin dar tiempo al agente al menos de 2:30m para responder.

    #     # RESTRICCIONES
    #     - Si el silencio del agente supera los **2:30m**, la calificación de **1.0** es automática, siempre y cuando el usuario abandone la interaccion por inactividad o esta se cierre deforma abrupta.
    #     - El cierre del chat sin una ""conclusión clara"" (confirmación de que no hay más dudas) se considera falla.

    #     # FORMATO DE RESPUESTA FINAL
    #     Solo entrega el valor float (ej. `0.0`, `1.0`, `2.0`).
    #     """        
    # )
    # didi_cal_refusal_to_attend_or_leaving_the_chat_description: str = Field(
    #     ...,
    #     description="Analizar el valor del campo 'didi_cal_refusal_to_attend_or_leaving_the_chat'; si el valor es 1.0, proporcionar una descripción breve del por qué de esta salida. Si el valor es 0.0, registrar 'No aplica'. El resultado debe entregarse en formato string."
    # )

    # 


  # didi_cal_lc_poor_linguistic_structural_or_clarity_quality: float = Field(
  #   ...,
  #   description="""
  #   # PERSONA
  #   Actúa como un Auditor de Calidad Lingüística y Lógica Comunicacional de alta precisión. Tu objetivo es medir la claridad, la estructura y la efectividad del mensaje del Agente (CSR), separando estrictamente la forma (ortografía, emojis, formato) del fondo (coherencia,hilo   conductor).
  #   # CONTEXTO
  #   Analizarás una conversación ignorando por completo las intervenciones etiquetadas como **Bot:** y **IVR:**. Te centrarás exclusivamente en el diálogo entre **Agente:** y **Cliente:** (quien puede ser Consumidor, Repartidor o Jefe de tienda).
  #   # TAREA
  #   Evaluar la comunicación del Agente asignando una calificación final en una escala del **1.0 al 5.0** (float), integrando la calidad gramatical con la estructura lógica del mensaje.
  #   # CADENA DE PENSAMIENTO (CHAIN-OF-THOUGHT)
  #   Para determinar la calificación de forma precisa, realiza internamente los siguientes pasos de análisis en orden:
  #   1. **Filtrado y Aislamiento:**
  #      - Identifica y extrae únicamente las respuestas emitidas por el **Agente:**. Omite el ruido de Bot e IVR.
  #   2. **Conteo e Identificación de Hallazgos (Checklist de Auditoría):**
  #      - **Errores de Forma (Sin alteración de sentido):** Cuenta fallas de tildes, digitación, letras omitidas/repetidas o uso incorrecto ocasional de mayúsculas/minúsculas. (¿Son 5 o más?).
  #      - **Errores de Forma Críticos (Con alteración de sentido):** Identifica palabras mal escritas o mal empleadas que cambien el significado original del mensaje o lo hagan incomprensible. (¿Hay 1 o más?).
  #      - **Uso de Emojis:** Detecta si el agente incluyó cualquier tipo de emoticón o emoji.
  #      - **Jerga o Abreviaciones:** Detecta el uso de modismos o abreviaciones no permitidas (ej. "pq", "tmb", "re", etc.) al menos 1 vez.
  #      - **Formato y Estructura:** - Identifica si existen párrafos densos (bloques de texto que tengan **6 o más líneas continuas**).
  #        - Detecta el uso de **mayúsculas sostenidas** (gritos virtuales).
  #   3. **Evaluación del Fondo (Coherencia e Hilo Conductor):**
  #      - Evalúa si el agente responde de manera lógica y directa a las dudas del cliente.
  #      - Identifica si el agente ignoró deliberada o accidentalmente preguntas explícitas del cliente.
  #      - Detecta si se enviaron mensajes sin sentido o totalmente desconectados del contexto de la conversación.
  #   4. **Aplicación de Reglas de Penalización Directa (Restricciones Máximas):**
  #      - Si ocurre CUALQUIERA de las siguientes condiciones, la calificación final **NO PUEDE SER MAYOR A 2.0**:
  #        * Presencia de 1 o más Emojis.
  #        * Presencia de 1 o más jergas o abreviaciones no permitidas.
  #        * Presencia de párrafos densos (6 o más líneas) o desorganizados.
  #        * Uso de mayúsculas sostenidas.
  #        * Presencia de 5 o más errores de ortografía menores (sin alteración de sentido).
  #        * Presencia de 1 solo error ortográfico que SÍ altere el sentido.
  #        * Si el agente ignora una o más preguntas explícitas del cliente.
  #        * Si el agente envía mensajes sin sentido frente a las consultas del cliente.
  #   5. **Asignación del Veredicto en la Escala:**
  #      - **5.0:** Comunicación excelente, clara y lógica. Cumple a la perfección con el fondo. Puede tener hasta un máximo de 4 errores menores de redacción/ortografía (tildes, typos) que no afecten la comprensión. *Nota: Si hay emojis, jerga, mayúsculas sostenidas o párrafos densos, es imposible asignar 5.0.*
  #      - **4.0:** Mensajes mayormente estructurados y claros. Presenta pequeños desvíos de enfoque o entre 1 y 4 errores ortográficos menores.
  #      - **3.0:** Estructura básica pero con debilidades. No incurre en penalizaciones automáticas, pero carece de total fluidez.
  #      - **2.0:** Comunicación deficiente o confusa. Se asigna de forma automática si se activa cualquiera de las penalizaciones de la sección de Restricciones, o si el agente muestra ideas inconexas e ignora parcialmente al cliente.
  #      - **1.0:** Incoherencia total, mensajes que carecen por completo de sentido en el contexto, o acumulación severa y negligente de múltiples penalizaciones.
  #   # FORMATO DE RESPUESTA FINAL
  #   Debes devolver únicamente el valor numérico correspondiente en formato float (por ejemplo: `5.0`, `4.0`, `2.0`, `1.0`). No agregues texto adicional, justificaciones o caracteres especiales.
  #   """
  # )  

  # didi_cal_lc_poor_linguistic_structural_or_clarity_quality_description: str = Field(
  #   ...,
  #   description="""
  #   # PERSONA
  #   Actúa como un Auditor de Calidad Lingüística y Lógica Comunicacional encargado de redactar el feedback de calibración.

  #   # TAREA
  #   Generar un reporte de diagnóstico conciso y técnico basado exclusivamente en la calificación obtenida en el campo 'didi_cal_lc_poor_linguistic_structural_or_clarity_quality' y los hallazgos del chat del Agente.

  #   # CADENA DE PENSAMIENTO (CHAIN-OF-THOUGHT)
  #   Para estructurar la descripción, sigue estos pasos lógicos:
  #   1. Evalúa el valor numérico recibido de la calificación.
  #   2. Si la nota es menor a 5.0, identifica textualmente en la conversación cuál o cuáles de las penalizaciones exactas se activaron.
  #   3. Redacta el veredicto de forma directa, citando el error específico (ej. la palabra con error, la jerga usada o la pregunta ignorada).

  #   # INSTRUCCIONES DE SALIDA (CRITERIOS DE SELECCIÓN)

  #   1. **Si el valor es MENOR o IGUAL a 4.0 (Presenta Penalizaciones o Fallas):**
  #      Proporciona una descripción técnica, específica y concisa identificando la falla exacta detectada en el chat del Agente. Debes especificar detalladamente si el motivo fue:
  #      - Presencia de 5 o más errores ortográficos menores (que no alteran el sentido, ej. falta de tildes o typos).
  #      - Presencia de 1 o más errores ortográficos que SÍ alteran el sentido original del mensaje.
  #      - Uso de emojis o emoticonos en el diálogo.
  #      - Uso de 1 o más jergas o abreviaciones no permitidas (ej. 'pq', 'tmb').
  #      - Mensajes visualmente desorganizados o párrafos densos (bloques de texto de 6 o más líneas).
  #      - Uso de mayúsculas sostenidas (gritos virtuales).
  #      - Envío de respuestas sin sentido o desconectadas de las preguntas/comentarios del cliente.
  #      - Ignorar una o más preguntas explícitas del cliente.

  #      *Ejemplo de salida esperada:* "El agente utilizó abreviaciones informales ('pq'), redactó un párrafo denso de más de 6 líneas e ignoró la pregunta explícita del usuario sobre el estado de su reembolso."

  #   2. **Si el valor es EXACTAMENTE 5.0 (Cumple):**
  #      Registra textualmente y sin variaciones la siguiente frase:
  #      "Cumple con los estándares de calidad lingüística y estructural."

  #   # RESTRICCIONES
  #   - La respuesta debe ser exclusivamente la cadena de texto descriptiva (string).
  #   - Sé sumamente específico: si detectas la falla, menciona textualmente qué regla se rompió y aporta el ejemplo si es posible.
  #   - No incluyas introducciones, saludos, ni etiquetas adicionales (como 'Diagnóstico:', 'Resultado:', etc.). Entrega el texto limpio.
  #   """
  # )

    didi_cal_lack_of_urgency_or_interest_in_helping: float = Field(
      ...,
      description="""
      # PERSONA
      Actúa como un Auditor de Calidad especializado en Psicología del Consumidor y Experiencia Emocional. Tu objetivo es asegurar que el cliente se sienta escuchado, comprendido y priorizado, no simplemente tratado como un número de ticket; algo inportante, la solución en ocaciones no depende del agente si no, de un escalamiento a otra area o escalamiento interno y esto se puede interpretar como una solución indirecta.
      # CONTEXTO
      Evaluarás la conexión emocional en un chat. Debes identificar momentos donde el usuario expresa frustración, enojo o tristeza y cómo el Agente (CSR) reacciona ante ello.
      # TAREA
      Analizar el reconocimiento de sentimientos y el sentido de urgencia, asignando un valor `float` según el cumplimiento.
      # CADENA DE PENSAMIENTO (CHAIN-OF-THOUGHT)
      Sigue este proceso de razonamiento para determinar la calificación:
      1. **Detección de 'Picos Emocionales' del Usuario:**
         - Identifica frases donde el usuario demuestre insatisfacción (ej. 'estoy harto', 'es el peor servicio', 'necesito esto ya', 'estoy decepcionado').
         - Identifica preguntas o comentarios que carguen una queja implícita o explícita.
      2. **Evaluación de la Respuesta del Agente (Reconocimiento):**
         - Ante un pico emocional: ¿El agente hizo un 'Statement of Empathy' (ej. 'Entiendo lo frustrante que esto debe ser')?
         - ¿El agente ignoró el comentario negativo y pasó directamente a un proceso transaccional/robótico?
      3. **Evaluación del Sentido de Urgencia:**
         - ¿El agente usó lenguaje que transmita prioridad? (ej. 'Voy a revisar esto de inmediato', 'Permíteme agilizar esto para ti').
         - ¿El tono se siente puramente transaccional o muestra interés real en la satisfacción?
      4. **Aplicación de Lógica de Penalización (Veredicto):**
         - **0.0 (Cumple):** El agente reconoció los sentimientos del cliente y mostró proactividad/urgencia y brindo alternativas.
         - **1.0 (No Cumple):** - El agente ignoró comentarios de insatisfacción o sentimientos negativos.
           - El tono fue puramente transaccional (robótico) ante una queja evidente.
           - El agente no respondió a una pregunta que contenía una expresión de insatisfacción.
         - **2.0 (No Aplica):** La interacción fue neutral, el cliente no mostró ninguna emoción o insatisfacción durante todo el chat.
      # RESTRICCIONES
      - **Excepción de Alternativas:** NO penalizar por no brindar alternativas (esto queda fuera de este parámetro según lineamientos).
      - El silencio ante una queja es falla automática (1.0).
      - **Salida:** Únicamente el número `float` (`0.0`, `1.0`, `2.0`).
      # FORMATO DE RESPUESTA FINAL
      Solo entrega el valor float.
      """        
    )
    didi_cal_lack_of_urgency_or_interest_in_helping_description: str = Field(
        ...,
        description="Analizar el valor del campo 'didi_cal_lack_of_urgency_or_interest_in_helping'; si el valor es 1.0, proporcionar una descripción breve del por qué de esta salida. Si el valor es 0.0, registrar 'No aplica'. El resultado debe entregarse en formato string."
    )