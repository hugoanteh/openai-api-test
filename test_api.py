from openai import OpenAI

client = OpenAI(api_key="TU_API_KEY_AQUI")

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Hola, ¿puedes confirmar que mi API funciona?"}]
)

print(response.choices[0].message.content)
