import os
import threading
from flask import Flask
import discord
from groq import Groq

# Servidor Flask para mantener activo el Web Service en Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

# Variables de entorno
TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Habilitar intents para que pueda leer contenido de mensajes y DMs
intents = discord.Intents.all()
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'Conectado como {bot.user}')

@bot.event
async def on_message(message):
    print(f"Mensaje recibido de {message.author}: {message.content}") # Imprime en consola para depurar

    # Ignorar mensajes propios
    if message.author == bot.user:
        return

    # Comprobar si es DM o mención
    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = bot.user.mentioned_in(message)

    if is_dm or is_mentioned:
        if is_mentioned:
            user_prompt = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        else:
            user_prompt = message.content.strip()

        if not user_prompt:
            return

        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un usuario humano normal en Discord. Responde de forma natural, breve y casual, como si estuvieras chateando con un amigo."
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            response_text = chat_completion.choices[0].message.content
            await message.reply(response_text)
        except Exception as e:
            print(f"Error al conectar con Groq: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot.run(TOKEN)
