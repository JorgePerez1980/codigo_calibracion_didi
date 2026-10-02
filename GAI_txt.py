from structured_prompt import *
from langchain_google_vertexai import ChatVertexAI,HarmBlockThreshold, HarmCategory
from langchain_core.messages import HumanMessage
from google.cloud import dlp_v2
import pandas as pd
import random
import re
from datetime import datetime
from environment import *
from split import TextSplitter


class TextAnalytics(object):

    def __init__(self, df: pd.DataFrame) -> None:

        self.df_used = df
        self.gai_project = GIA_PROJECT
        self.gai_location = GIA_LOCATION
        self.gai_model = GIA_MODEL
        try:
            self.csat = float(self.df_metadata['custom_data_57'][0])
        except:
            self.csat = float(CSAT)

        try:    
            self.tiempo_maximo_espera = float(self.df_used['custom_data_57'][0])
        except:
            self.tiempo_maximo_espera = float(WAITING_TIME)
            
        self.max_output_tokens = int(GIA_MAX_OUTPUT_TOKENS)
        self.temperature = float(GIA_TEMPERATURE)
        self.top_p = float(GIA_TOP_P)
        self.top_k = int(GIA_TOP_K)
        self.candidate_count = int(GIA_CANDIDATE_COUNT)
        self.text_var = GIA_TEXT_VAR
        self.attempt = 0


    @staticmethod
    def genereate_random_numbers(longitud: int) -> str:
        rango_inicio = 10**(longitud-1)
        rango_fin = (10**longitud) - 1
        return str(random.randint(rango_inicio, rango_fin)).zfill(longitud)

    def replace_number(self, match: set[str]) -> str:
        numero_telefono = match.group()
        numero_aleatorio = self.genereate_random_numbers(len(numero_telefono))
        return numero_aleatorio

    def anomizer_number(self, texto: str) -> str:
        # Expresión regular para detectar números de 1 a 10 dígitos
        # que no estén precedidos ni seguidos por signos de moneda o palabras relacionadas
        regex_numero_telefono = re.compile(
            r'\b\d{1,12}\b'
        )

        # Expresión regular para detectar valores monetarios
        regex_1 = re.compile(
            r'(?<!\d)\b\d{1,12}\b\s*([$€%]|€)|(\$|€)\s*\d{1,12}|\d{1,12}\s*(euros|pesos|dólares|porcentaje|céntimos)|(?:[01]?\d|2[0-3]):[0-5]\d|\[\d{2}:\d{2}\.\d{2}\]', re.IGNORECASE)

        # Encontrar todos los números relacionados con valores monetarios
        ignorar_matches = {match.group() for match in regex_1.finditer(texto)}

        # Función de reemplazo mejorada que verifica si el número está en la lista de ignorados
        def replace_numbers(match: set[str]):
            numero = match.group()
            if any(numero in match for match in ignorar_matches):
                return numero
            else:
                return self.replace_number(match)

        # Reemplazar todos los números de teléfono en el texto con números aleatorios
        texto_anonimizado = regex_numero_telefono.sub(replace_numbers, texto)
        return texto_anonimizado

    def redact_sensitive_data(self, text_to_redact: str) -> str:
        # Crear un cliente de DLP
        dlp = dlp_v2.DlpServiceClient(
            client_options={"quota_project_id": self.gai_project})

        # Definir el proyecto de Google Cloud donde está habilitada la API
        parent = f"projects/{self.gai_project}"

        # Configurar la información de identificación personal (PII) a buscar
        info_types = [
            {"name": "FIRST_NAME"},
            {"name": "LAST_NAME"},
            {"name": "PHONE_NUMBER"},
            {"name": "DATE_OF_BIRTH"},
            {"name": "CREDIT_CARD_NUMBER"},
            {"name": "IBAN_CODE"},
            {"name": "SWIFT_CODE"},
            {"name": "LOCATION"},
            {"name": "CREDIT_CARD_TRACK_NUMBER"},
            {"name": "MEDICAL_RECORD_NUMBER"},
            {"name": "US_SOCIAL_SECURITY_NUMBER"},
            {"name": "UK_NATIONAL_INSURANCE_NUMBER"},
            {"name": "IP_ADDRESS"},
            {"name": "MAC_ADDRESS"},
            {"name": "URL"},
            {"name": "DOMAIN_NAME"},
            {"name": "EMAIL_ADDRESS"},
        ]

        # Diccionario para las transformaciones personalizadas
        transformaciones_personalizadas = {
            "FIRST_NAME": "[FIRST_NAME]",
            "LAST_NAME": "[LAST_NAME]",
            "PHONE_NUMBER": "[PHONE_NUMBER]",
            "EMAIL_ADDRESS": "[EMAIL_ADDRESS]",
        }

        transformations = []
        for info_type in info_types:
            if info_type["name"] in transformaciones_personalizadas:
                transformations.append({
                    "info_types": [info_type],
                    "primitive_transformation": {
                        "replace_config": {
                            "new_value": {
                                "string_value": transformaciones_personalizadas[info_type["name"]]
                            }
                        }
                    }
                })
            else:
                transformations.append({
                    "info_types": [info_type],
                    "primitive_transformation": {
                        "replace_with_info_type_config": {}
                    }
                })

        deidentify_config = {
            "info_type_transformations": {
                "transformations": transformations
            }
        }

        inspect_config = {
            "info_types": info_types
        }

        item = {"value": text_to_redact}

        # Llamado de la API
        response = dlp.deidentify_content(
            request={
                "parent": parent,
                "inspect_config": inspect_config,
                "deidentify_config": deidentify_config,
                "item": item
            }
        )

        # Devolver el texto redactado
        texto_anonimizado = self.anomizer_number(response.item.value)

        return texto_anonimizado

    def prompt(self) -> None:
        self.chat = str(self.df_used[self.text_var][0])

        self.content_text ="""
            **CONTEXTO**
            Como auditor de calidad experto, evalúa y analiza los textos de los chats del servicio al cliente de DiDi. El objetivo es identificar áreas de mejora en el desempeño de los agentes, evaluar la efectividad en la resolución de requerimientos y mejorar la satisfacción del cliente para garantizar una experiencia de alta calidad. 

            # Steps

            1. **Análisis del Desempeño del Agente**: Revisa los chats para evaluar la habilidad del agente en cumplir con los protocolos de servicio, uso del lenguaje, empatía, y profesionalismo.
            2. **Evaluación de la Efectividad**: Analiza cómo los requerimientos del cliente fueron atendidos y si las soluciones proporcionadas por los agentes fueron adecuadas y eficientes.
            3. **Identificación de Áreas de Mejora**: Detecta patrones o incidencias repetitivas que puedan indicar áreas donde los agentes necesiten más formación o cambios en los procedimientos.
            4. **Evaluación de la Satisfacción del Cliente**: Investiga si el cliente quedó satisfecho con la interacción, basando el análisis en expresiones de satisfacción, resolución de problemas y actitud del cliente al finalizar el chat.

            # Output Format

            El análisis debe ser presentado como un informe en JSON 
            # Notes

            Considere todas las variantes posibles del lenguaje que un cliente podría utilizar y reconozca regionalismos o jerga.
            Tenga en cuenta los diferentes tipos de servicios que ofrece DiDi y cómo pueden impactar en la naturaleza del chat.
            En caso de falta de claridad en ciertos aspectos del chat, asuma contextos razonables para completar el análisis.
        **INSTRUCCIONES**
            Evalúa las interacciones de chat con máximo detalle y precisión en los textos chat de los centros de atención de DiDi. Realiza un análisis experto para identificar aspectos clave que impactan la experiencia y satisfacción del cliente en servicios de entrega de alimentos, productos no perecederos, transporte de pasajeros y finanzas.

            - Considera factores como:
            - Claridad y precisión de la información proporcionada por el agente.
            - Empatía demostrada.
            - Sentido de urgencia transmitido para resolver las necesidades del cliente.
            - Capacidad para gestionar las solicitudes de manera efectiva desde el primer contacto.

            - Proporciona retroalimentación detallada y accionable para mejorar el desempeño de los agentes.
            - Facilita la toma de decisiones informadas para la empresa mediante los datos obtenidos.

            # Roles Involucrados

            - **Bot**: Automatiza respuestas predefinidas y recopila información básica.
            - **Agente**: Interactúa directamente con el cliente, proporcionando asistencia personalizada.
            - **Cliente**: Solicita ayuda o información sobre servicios, este puede interactuar como sub rol ‘Cliente consumidor’, ‘Repartidor’ o ‘Jefe de tienda’.

            # Steps

            1. **Revisión del Chat**: Lee detenidamente la interacción completa, asegurándote de identificar quién es el Bot, el Agente y el Cliente teniendo presente los sub roles ‘Cliente consumidor’, ‘Repartidor’ o ‘Jefe de tienda’ en cada segmento del mensaje.
            
            2. **Análisis de Aspectos Clave**:
            - **Claridad y precisión**: Evalúa si la información proporcionada resuelve la consulta sin confusiones.
            - **Empatía**: Identifica instancias de demostración de comprensión y preocupación genuina.
            - **Sentido de Urgencia**: Observa cómo se maneja el tiempo en la respuesta y resolución.
            - **Gestión Efectiva**: Revisa si la solicitud fue resuelta en el primer intento sin necesidad de escalamiento.

            3. **Retroalimentación**: Desarrolla comentarios concretos, con observaciones específicas de áreas de mejora y cómo pueden implementarse cambios positivos.

            # Output Format

            Proporciona un informe estructurado que incluya:
            - Nombre del Agente (si corresponde)
            - Evaluación por Aspecto Clave: Claridad, Empatía, Urgencia, Gestión.
            - Retroalimentación Detallada: Sugerencias para mejoras.

            # Examples

            **Ejemplo de Chat Análisis:**

            --- 

            **Chat Detalle**: [Diálogo completo entre Bot, Agente y Cliente]

            **Análisis Evaluación**:
            - **Claridad**: [El texto ofrecido por el agente fue claro, utilizó términos sencillos para explicar el procedimiento.]
            - **Empatía**: [El agente mostró comprensión al usar expresiones como "Entiendo su preocupación...".]
            - **Urgencia**: [Aunque el agente respondió rápidamente, la solución se retrasó debido a pasos adicionales no previstos.]
            - **Gestión Efectiva**: [La solicitud fue resuelta sin transferir a otro agente.]

            **Retroalimentación**: 
            "Incluir ejemplos anticipados de problemas similares para acortar el tiempo de respuesta en futuras interacciones.''

            ---

            (Note: Un análisis completo debe proporcionar un reporte más extenso y detallado de cada interacción específica basada en el extracto del chat.) 

            # Notes

            - Asegúrate de que el marco temporal para cada interacción y respuesta esté documentado.
            - Si un agente no puede resolver un problema inmediatamente, evalúa la efectividad de la redirección o escalamiento del caso.
            - Toma en cuenta las especificidades de cada servicio (alimentos, transporte, etc.) ya que pueden influir en las prioridades de la interacción.

            
            """

    def generate(self) -> None:
        self.prompt()
        safety_settings = {
            HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }

        model = ChatVertexAI(model=self.gai_model, project=self.gai_project, location="us-central1",
                             temperature=self.temperature, top_p=self.top_p,
                             top_k=self.top_k, max_output_tokens=self.max_output_tokens,safety_settings=safety_settings,
                             )

        message = HumanMessage(
            content=[
                {
                    "type": "text", 
                    "text": self.content_text
                },
                {
                    "type": "text", "text":
                    "Chat:"
                    "\n\n"
                    f"{self.chat}"
                 }
            ],
        )

        ### Separar el texto por roles en la interacción
        splitter = TextSplitter(self.chat)
        bot, client, agent = splitter.split()

        message_agent = HumanMessage(
            content=[
                {
                    "type": "text", 
                    "text": self.content_text
                },
                {
                    "type": "text", "text":
                    "Chat solo con el texto del agente:"
                    "\n\n"
                    f"{agent}"
                 }
            ],
        )

        structured_model1 = model.with_structured_output(
            StructuredPrompt1, include_raw=True)
       

        print(f'structured_llm1 -> {len(StructuredPrompt1.__fields__)}')
        response1 = structured_model1.invoke([message])
        
        # --- NUEVA LÓGICA DE VALIDACIÓN ---
        if response1["parsed"] is not None:
            # Si la IA respondió correctamente, extraemos los datos
            df_final = pd.DataFrame([response1["parsed"].__dict__])
        else:
            # Si la IA falló, creamos un DataFrame con valores vacíos para no romper el proceso
            print(f"⚠️ Error: La IA no pudo parsear el chat. Creando fila vacía.")
            # Creamos un diccionario con las columnas de StructuredPrompt1 pero vacías
            vacio = {key: "Error: No se pudo analizar" for key in StructuredPrompt1.__fields__.keys()}
            df_final = pd.DataFrame([vacio])
        # ----------------------------------

        # Para los tokens, también blindamos por si 'raw' viene incompleto
        try:
            usage = response1["raw"].usage_metadata
            self.df_used['prompt_token_count'] = usage.get("input_tokens", 0)
            self.df_used['candidates_token_count'] = usage.get("output_tokens", 0)
            self.df_used['total_token_count'] = usage.get("total_tokens", 0)
        except Exception as e:
            print(f"No se pudieron obtener metadatos de tokens: {e}")
            self.df_used['total_token_count'] = 0

        now = pd.Timestamp(datetime.now())
        now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
        self.df_used['process_timestamp'] = now

        # Unimos los metadatos con el análisis (si df_final existe)
        df_final = pd.concat([self.df_used.reset_index(drop=True), df_final.reset_index(drop=True)], axis=1)

        return df_final

    def processing(self) -> pd.DataFrame:

        df = self.generate()

        return df
