from dotenv import load_dotenv
from openai import OpenAI
import discord, os

# Cargar variables del entorno (.env)
load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")
TOKEN = os.getenv("TOKEN")

if not OPENAI_KEY:
    raise RuntimeError("❌ Falta OPENAI_KEY en el archivo .env")
if not TOKEN:
    raise RuntimeError("❌ Falta TOKEN en el archivo .env")

# Crear cliente de OpenAI
oa_client = OpenAI(api_key=OPENAI_KEY)

# Definir la guía de preguntas
GUIDE = [
    "¿Podrías contarme cómo es un día típico en tu trabajo?",
    "¿Qué es lo que más disfrutas o te motiva de tus actividades diarias?",
    "¿Qué tipo de dificultades o frustraciones enfrentas en tu rol?",
    "¿Cómo sueles tomar decisiones importantes en tu día a día laboral?",
    "Si pudieras cambiar algo en tu entorno de trabajo, ¿qué sería y por qué?"
]

# Diccionario para guardar el progreso de cada usuario
user_sessions = {}

# --- FUNCIONES ---

def interview_agent(user_id, user_input):
    """
    Lógica del agente entrevistador:
    - Usa la guía de 5 preguntas.
    - Repregunta según la respuesta.
    - Avanza automáticamente cuando corresponde.
    """

    # Recuperar progreso del usuario o iniciar nuevo
    session = user_sessions.get(user_id, {"index": 0, "history": []})
    index = session["index"]
    history = session["history"]

    # Si terminó todas las preguntas
    if index >= len(GUIDE):
        return "Gracias por tu tiempo. La entrevista ha terminado 🙏"

    # Construir el historial del chat
    messages = [
        {
            "role": "system",
            "content": (
                "Eres un investigador de mercados especializado en entrevistas a profundidad. "
                "Siempre empiezas tus respuestas con 'Hola', no empieces con 'Quiero decirte que todo está bien' "
                "Tu objetivo es comprender emociones y motivaciones, usando un tono empático y profesional. "
                "Haz repreguntas naturales para profundizar en la respuesta del usuario, pero no cambies de tema. "
                "Si ya has profundizado lo suficiente, pasa a la siguiente pregunta de la guía."
            ),
        }
    ]

    # Agregar historial previo
    messages.extend(history)

    # Añadir la última respuesta del usuario
    messages.append({"role": "user", "content": user_input})

    # Contexto con la pregunta actual
    messages.append({
        "role": "system",
        "content": f"La pregunta actual de la guía es: '{GUIDE[index]}'. "
                   "Repregunta si es necesario, o si ya se exploró suficiente, avanza a la siguiente."
    })

    # Llamada al modelo
    completion = oa_client.chat.completions.create(
        model="gpt-4o",
        messages=messages
    )

    response = completion.choices[0].message.content

    # Actualizar historial
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": response})

    # Decidir si pasar a la siguiente pregunta
    if any(phrase in response.lower() for phrase in ["siguiente pregunta", "ahora cuéntame", "por otro lado"]):
        index += 1

    # Guardar progreso
    user_sessions[user_id] = {"index": index, "history": history}

    return response


# --- DISCORD BOT CONFIG ---

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"✅ Bot conectado como: {client.user}")

@client.event
async def on_message(message):
    # Ignorar mensajes del mismo bot
    if message.author == client.user:
        return

    user_id = str(message.author.id)

    # Saludo básico
    if message.content.startswith("$hello"):
        await message.channel.send("👋 ¡Hola! Estoy listo para empezar la entrevista.")

    # Iniciar o continuar entrevista
    if message.content.startswith("$start"):
        user_sessions[user_id] = {"index": 0, "history": []}
        await message.channel.send("Hola. Gracias por participar. Empecemos:")
        await message.channel.send(GUIDE[0])

    # Capturar respuestas del usuario
    elif user_id in user_sessions:
        response = interview_agent(user_id, message.content)
        await message.channel.send(response)

client.run(TOKEN)