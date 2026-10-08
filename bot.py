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
    print(f'Conectado como {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        user_prompt = message.content.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()
        
        try:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "user": "Eres un asistente útil en Discord."},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.3-70b-versatile",
            )
            response_text = chat_completion.choices[0].message.content
            await message.reply(response_text)
        except Exception as e:
            await message.reply(f"Error al conectar con Groq: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.start()
    bot.run(TOKEN, bot=False)
