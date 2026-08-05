import os
import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup

# ===== MANTER 24H ONLINE =====
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "✅ BOT ONLINE 24H!"

def manter_online():
    app.run(host='0.0.0.0', port=8080)

Thread(target=manter_online).start()
# =============================

import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SERPER_API_KEY = "2bc35519fe409f4d50920fbf08f7679414f9026c"

PREFIXO = "!"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents, help_command=None)

async def buscar_google(pergunta):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    try:
        resp = requests.post(url, json={"q": pergunta}, headers=headers, timeout=10)
        return resp.json().get("organic", [])[:3]
    except:
        return None

@bot.command()
async def buscar(ctx, *, pergunta):
    await ctx.send(f"🔍 Buscando: {pergunta}...")
    resultados = await buscar_google(pergunta)
    if not resultados:
        await ctx.send("❌ Não encontrei resultados.")
        return
    texto = f"🔎 **Resultados para: {pergunta}**\n\n"
    for i, r in enumerate(resultados, 1):
        texto += f"**{i}.** {r.get('title', 'Sem título')}\n🔗 {r.get('link', '')}\n{r.get('snippet', '')[:150]}...\n\n"
    await ctx.send(texto[:2000])

@bot.command()
async def ler(ctx, link: str):
    if not link.startswith("http"):
        await ctx.send("⚠️ Manda o link completo (https://...)")
        return
    try:
        await ctx.send("🔍 Entrando no site...")
        resp = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code != 200:
            await ctx.send(f"❌ Erro: código {resp.status_code}")
            return
        sopa = BeautifulSoup(resp.text, "html.parser")
        titulo = sopa.title.string if sopa.title else "Sem título"
        await ctx.send(f"🌐 **{titulo}**\n📝 {sopa.get_text(strip=True)[:400]}...")
    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)}")

@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="24h online ☁️"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    if message.content.startswith("!"):
        return
    texto = message.content.lower().strip()
    if "?" in texto and not any(p in texto for p in ["quem", "o que", "onde", "quando", "como", "por que", "qual"]):
        await message.channel.send(random.choice(["✅ Sim", "❌ Não"]))
        return

bot.run(DISCORD_TOKEN)
