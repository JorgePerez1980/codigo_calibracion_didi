import re

class TextSplitter:
    def __init__(self, text: str):
        self.text = str(text)

    def split(self) -> tuple[str, str, str]:


        # Expresiones regulares para separar por roles
        pattern_bot = r"Bot: (.*?)(?=\b(Bot:|Cliente:|Agente:|$))"
        pattern_client = r"Cliente: (.*?)(?=\b(Bot:|Cliente:|Agente:|$))"
        pattern_agent = r"Agente: (.*?)(?=\b(Bot:|Cliente:|Agente:|$))"

        # Extraer textos por rol
        bot_text = re.findall(pattern_bot, self.text, re.DOTALL)
        client_text = re.findall(pattern_client, self.text, re.DOTALL)
        agent_text = re.findall(pattern_agent, self.text, re.DOTALL)

        # Limpiar resultados
        bot_text = ' '.join(t[0].strip() for t in bot_text)
        client_text = ' '.join(t[0].strip() for t in client_text)
        agent_text = ' '.join(t[0].strip() for t in agent_text)

        return bot_text, client_text, agent_text