import discord
from discord.ext import commands
import random
import requests
from bs4 import BeautifulSoup

# ========== TOKEN + CHAVE JÁ COLOCADAS ==========
DISCORD_TOKEN = "MTUzNDQxNTM3ODM2MzcxMTUyOA.GzmdWd.ivCnffryB1oq0RXEAFD1bWouSFcXPlATxl_hr0"
SERPER_API_KEY = "2bc35519fe409f4d50920fbf08f7679414f9026c"

PREFIXO = "!"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIXO, intents=intents, help_command=None)

# ========== BUSCA NO GOOGLE ==========
async def buscar_google(pergunta):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        resp = requests.post(url, json={"q": pergunta}, headers=headers, timeout=10)
        dados = resp.json()
        return dados.get("organic", [])[:3]
    except:
        return None

@bot.command()
async def buscar(ctx, *, pergunta):
    """!buscar [o que quer saber] → pesquisa no Google"""
    await ctx.send(f"🔍 Buscando: {pergunta}...")
    resultados = await buscar_google(pergunta)
    
    if not resultados:
        await ctx.send("❌ Não encontrei resultados.")
        return

    texto = f"🔎 **Resultados para: {pergunta}**\n\n"
    for i, r in enumerate(resultados, 1):
        texto += f"**{i}.** {r.get('title', 'Sem título')}\n"
        texto += f"🔗 {r.get('link', '')}\n"
        texto += f"{r.get('snippet', '')[:150]}...\n\n"
    
    await ctx.send(texto[:2000])

# ========== LER SITE ==========
@bot.command()
async def ler(ctx, link: str):
    """!ler [link] → lê e resume o site"""
    if not link.startswith("http"):
        await ctx.send("⚠️ Manda o link completo (https://...)")
        return
    try:
        await ctx.send("🔍 Entrando no site...")
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(link, headers=headers, timeout=10)
        if resp.status_code != 200:
            await ctx.send(f"❌ Erro: código {resp.status_code}")
            return
        sopa = BeautifulSoup(resp.text, "html.parser")
        titulo = sopa.title.string if sopa.title else "Sem título"
        texto = sopa.get_text(strip=True)[:400]
        await ctx.send(f"🌐 **{titulo}**\n📝 {texto}...")
    except Exception as e:
        await ctx.send(f"❌ Erro: {str(e)}")

# ========== COMANDOS BÁSICOS ==========
@bot.event
async def on_ready():
    print(f"✅ BOT ONLINE: {bot.user}")
    await bot.change_presence(activity=discord.Game(name="buscando 🔍"))

@bot.command()
async def ajuda(ctx):
    await ctx.send("""
😎 **JOSEFP — TUDO PRONTO!** 🔍📖

!buscar [pergunta] → pesquisa no Google 🌐
!ler [link] → lê e resume um site 📖
!ola → te cumprimento
!ping → teste 🏓
**Pergunta com ? → respondo Sim/Não!** ✅❌
    """)

@bot.command()
async def ola(ctx):
    await ctx.send("😎 E aí! Tudo bem contigo?")

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency*1000)}ms")

# ========== CONVERSAS + SIM/NÃO ==========
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)
    if message.content.startswith("!"):
        return

    texto = message.content.lower().strip()

    # Sim/Não automático
    if "?" in texto and not any(p in texto for p in ["quem", "o que", "onde", "quando", "como", "por que", "qual"]):
        await message.channel.send(random.choice(["✅ Sim", "❌ Não"]))
        return

    # Conversas simples
    if any(p in texto for p in ["olá", "ola", "e aí"]):
        await message.channel.send("😎 Tudo bem, parceiro?")

# ========== LIGAR O BOT ==========
bot.run(DISCORD_TOKEN)
