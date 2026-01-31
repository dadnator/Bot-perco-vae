import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- CONFIGURATION ---
# Assure-toi que cette variable est bien dans l'onglet "Environment" de Render
token = os.environ.get('TOKEN_BOT_DISCORD')

PERCO_CHANNEL_ID = 1446103983046266880 
CONFIRM_CHANNEL_ID = 1446104046300696598
TARGET_GUILD_ID = 1445883050163703904

target_guild = discord.Object(id=TARGET_GUILD_ID)
SETUP_IMAGE_URL = "https://i.imgur.com/8setyQq.png" 

# --- RÔLES ET BOUTONS ---
ROLES_PING = {
    "Sleeping": {"id": 1446103551951638570, "label": " Sleeping", "emoji": "<:TheSleepingBlossoms:1446119822260965436>"},
    "La Bande": {"id": 1446104186533056684, "label": " La Bande", "emoji": "<:LABANDE:1446119877801672755>"},
    "Skypiea'": {"id": 1447284168693383229, "label": " Skypiea'", "emoji": "<:Skypea:1447298600169242624>"},
}

# --- INITIALISATION DU BOT AVEC INTENTS ---
intents = discord.Intents.default()
intents.message_content = True  # CRUCIAL pour les commandes
intents.members = True          # Pour voir qui clique

bot = commands.Bot(command_prefix="/", intents=intents)

# --- CLASSES POUR L'INTERFACE ---
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
        await interaction.response.defer(ephemeral=True)
        perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
        
        if perco_channel:
            role_mention = f"<@&{self.role_id}>"
            user_display_name = interaction.user.display_name
            
            alert_content = f"{role_mention} **Votre percepteur est attaqué !** (Pingé par **{user_display_name}**)"
            
            await perco_channel.send(
                content=alert_content,
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            await interaction.followup.send(f"✅ Alerte envoyée pour **{self.role_name}** !", ephemeral=True)
        else:
            await interaction.followup.send("❌ Salon introuvable.", ephemeral=True)

class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None) # Timeout=None pour que les boutons restent actifs
        for role_key, role_data in ROLES_PING.items():
            self.add_item(PingButton(role_id=role_data["id"], role_name=role_key, label=role_data["label"], emoji_btn=role_data["emoji"]))

# --- ÉVÉNEMENTS ---
@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    
    try:
        # On rend la vue persistante
        bot.add_view(PingAttackView())
        
        # Synchronisation UNIQUEMENT sur le serveur cible pour éviter l'erreur 429
        print("⏳ Synchronisation des commandes slash...")
        synced = await bot.tree.sync(guild=target_guild) 
        print(f"✅ {len(synced)} commandes synchronisées sur le serveur.")
        
    except Exception as e:
        print(f"❌ Erreur au démarrage : {e}")

# --- COMMANDE SETUP ---
@bot.tree.command(name="setup_ping_button", description="Envoie le panneau d'alerte.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    setup_embed = discord.Embed(
        title="📢 Alerte Percepteur",
        description="Cliquez sur votre groupe pour signaler une attaque.",
        color=discord.Color.red()
    )
    if SETUP_IMAGE_URL:
        setup_embed.set_image(url=SETUP_IMAGE_URL)
    
    await interaction.channel.send(embed=setup_embed, view=PingAttackView())
    await interaction.response.send_message("✅ Panneau envoyé.", ephemeral=True)

# --- LANCEMENT ---
if __name__ == "__main__":
    keep_alive()
    if token:
        bot.run(token)
    else:
        print("❌ ERREUR : Le TOKEN n'est pas trouvé dans les variables d'environnement.")
