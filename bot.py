import os
import threading
from flask import Flask
import discord
from groq import Groq

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

TOKEN = os.environ.get("DISCORD_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = discord.Client()

@bot.event
async def on_ready():
    print(f'=== BOT ONLINE: {bot.user} ===', flush=True)

@bot.event
async def on_message(message):
    # Imprime CUALQUIER mensaje que llegue a la cuenta para depurar en tiempo real
    print(f"[RECOGIDO] De: {message.author} | Tipo de canal: {type(message.channel)} | Contenido: '{message.content}'", flush=True)

    # Ignorar mensajes de tu propia cuenta
    if message.author == bot.user:
        return

    # Comprobar si es un chat privado (DM individual o de grupo)
    is_dm = isinstance(message.channel, (discord.DMChannel, discord.GroupChannel))
    is_mentioned = bot.user.mentioned_in(message)

    if is_dm or is_mentioned:
        if is_mentioned:
            user_prompt = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        else:
            user_prompt = message.content.strip()

        if not user_prompt:
            print("--> Mensaje vacío o solo mención sin texto.", flush=True)
            return

        print(f"--> Procesando respuesta con Groq para {message.author}...", flush=True)

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
                model="llama-3.1-8b-instant",
            )
            response_text = chat_completion.choices[0].message.content
            
            # Enviar la respuesta
            await message.reply(response_text)
            print(f"--> Respuesta enviada a {message.author} con éxito.", flush=True)
            
        except Exception as e:
            print(f"!!! Error en Groq/Discord: {e}", flush=True)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    bot.run(TOKEN)
