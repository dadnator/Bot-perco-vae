import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- VOS CONSTANTES ---
token = os.environ['TOKEN_BOT_DISCORD']
PERCO_CHANNEL_ID = 1446103983046266880 
TARGET_GUILD_ID = 1445883050163703904
target_guild = discord.Object(id=TARGET_GUILD_ID)

SETUP_IMAGE_URL = "https://i.imgur.com/8setyQq.png" 

ROLES_PING = {
    "Sleeping": {"id": 1446103551951638570, "label": " Sleeping", "emoji": "<:TheSleepingBlossoms:1446119822260965436>"},
    "La Bande": {"id": 1446104186533056684, "label": " La Bande", "emoji": "<:LABANDE:1446119877801672755>"},
    "Skypiea'": {"id": 1447284168693383229, "label": " Skypiea'", "emoji": "<:Skypea:1447298600169242624>"},
    "Purge": {"id": 1473043558704480318, "label": " Purge", "emoji": "⚠️"},
}


intents = discord.Intents.default()
intents.members = True # Nécessaire pour display_name
bot = commands.Bot(command_prefix="/", intents=intents)

# --- 1. CLASSE POUR LE BOUTON INDIVIDUEL ---
class PingButton(Button):
    def __init__(self, role_id: int, role_name: str, label: str, emoji_btn: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.danger,
            emoji=emoji_btn,
            custom_id=f"ping_button_{role_name.lower().replace(' ', '_')}" 
        )
        self.role_id = role_id
        self.role_name = role_name
        
    async def callback(self, interaction: discord.Interaction):
        # OPTIMISATION : On répond immédiatement pour éviter le timeout/rate-limit
        try:
            perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
            if not perco_channel:
                return await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)

            role_mention = f"<@&{self.role_id}>"
            user_display_name = interaction.user.display_name
            
            # Envoi du ping dans le salon
            await perco_channel.send(
                content=f"{role_mention} **Votre percepteur est attaqué !** (Pingé par **{user_display_name}**)",
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            # Confirmation à l'utilisateur
            await interaction.response.send_message(f"✅ Alerte envoyée pour **{self.role_name}** !", ephemeral=True)
            
        except discord.errors.HTTPException as e:
            if e.status == 429:
                print("🛑 Rate limit détecté lors d'un clic bouton.")

# --- 2. CLASSE VIEW ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_key, role_data in ROLES_PING.items():
            self.add_item(PingButton(role_id=role_data["id"], role_name=role_key, label=role_data["label"], emoji_btn=role_data["emoji"]))

# --- 3. ÉVÉNEMENTS ---
@bot.event
async def on_ready():
    print(f"✅ Bot Connecté : {bot.user}")
    
    # PAUSE DE SÉCURITÉ : Laisse le bot se stabiliser avant de synchroniser
    await asyncio.sleep(5)
    
    try:
        bot.add_view(PingAttackView())
        # UNE SEULE SYNCHRO : On synchronise uniquement sur le serveur cible
        await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées sur le serveur.")
    except Exception as e:
        print(f"❌ Erreur Sync : {e}")

# --- 4. COMMANDE SETUP ---
@bot.tree.command(name="setup_ping_button", description="Envoie l'embed avec les boutons.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    setup_embed = discord.Embed(
        title="📢 Un Perco Attaqué ",
        description="**CLIQUEZ UNE FOIS** sur le bouton pour alerter.",
        color=discord.Color.blue()
    )
    if SETUP_IMAGE_URL:
        setup_embed.set_image(url=SETUP_IMAGE_URL)
    
    await interaction.channel.send(embed=setup_embed, view=PingAttackView())
    await interaction.response.send_message("✅ Panneau envoyé.", ephemeral=True)

# --- LANCEMENT ---
keep_alive()
try:
    bot.run(token)
except Exception as e:
    print(f"❌ Erreur fatale au lancement : {e}")
