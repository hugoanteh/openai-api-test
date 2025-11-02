from openai import OpenAI
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

# Leer API key desde la variable de entorno
api_key = os.getenv("OPENAI_API_KEY")

# Crear cliente
client = OpenAI(api_key=api_key)

# Enviar mensaje de prueba
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "Hola, ¿puedes confirmar que mi API funciona?"}
    ]
)

# Mostrar la respuesta del modelo
print(response.choices[0].message.content)