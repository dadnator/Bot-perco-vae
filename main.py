import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- CONFIGURATION ---
token = os.environ['TOKEN_BOT_DISCORD']
PERCO_CHANNEL_ID = 1446103983046266880 
TARGET_GUILD_ID = 1445883050163703904
target_guild = discord.Object(id=TARGET_GUILD_ID)

SETUP_IMAGE_URL = "https://i.imgur.com/8setyQq.png" 

# --- CONFIGURATION DES LIGNES ---
# row 0 : La Bande
# row 1 : Pantheon
# row 2 : Rixe
# row 3 : Sleeping, Purge, Légion
# row 4 : Yaco, La Secte, Prisme

# Organisation des rôles par ligne (row de 0 à 4)
ROLES_PING = {
    # Ligne 1 : La Bande
    "La Bande": {"id": 1446104186533056684, "label": " La Bande", "emoji": "<:LABANDE:1446119877801672755>", "row": 0},
    "La Bande2": {"id": 1492223642262700122, "label": " La Bande2", "emoji": "<:LABANDE:1446119877801672755>", "row": 0},
    
    # Ligne 2 : Pantheon
    "Pantheon'": {"id": 1447284168693383229, "label": " Pantheon", "emoji": "<:Pantheon:1488089492580732948>", "row": 1},
    "Pantheon'2": {"id": 1492223577351786537, "label": " Pantheon2", "emoji": "<:Pantheon:1488089492580732948>", "row": 1},
    
    # Ligne 3 : Rixe
    "Rixe": {"id": 1494432888295264316, "label": " Rixe", "emoji": "<:Rixe:1494555970427158619>", "row": 2},
    "Rixe2": {"id": 1494439212483870790, "label": " Rixe2", "emoji": "<:Rixe:1494555970427158619>", "row": 2},
    
    # Ligne 4 : Sleeping, Purge, Légion
    "Sleeping": {"id": 1446103551951638570, "label": " Sleeping", "emoji": "<:TheSleepingBlossoms:1446119822260965436>", "row": 3},
    "Purge": {"id": 1473043558704480318, "label": " Purge", "emoji": "<:Purge:1473218519997878416>", "row": 3},
    "Légion": {"id": 1478171491966128205, "label": " Légion", "emoji": "<:Legion:1478305376201085123>", "row": 3},
    
    # Ligne 5 : Yaco, La Secte, Prisme
    "Yaco": {"id": 1478170611778982069, "label": " Yaco", "emoji": "<:Yaco:1478304478858842222>", "row": 4},
    "La Secte": {"id": 1491550881492107264, "label": " La Secte", "emoji": "<:Lasecte:1491653111230500945>", "row": 4},
    "Prisme": {"id": 1446129172064764020, "label": " Prisme", "emoji": "<:gotham:1451529054925881354>", "row": 4},
}

intents = discord.Intents.default()
intents.members = True 
bot = commands.Bot(command_prefix="/", intents=intents)

# --- 1. CLASSE POUR LE BOUTON ---
class PingButton(Button):
    def __init__(self, role_id: int, role_name: str, label: str, emoji_btn: str, row: int):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.danger,
            emoji=emoji_btn,
            custom_id=f"ping_button_{role_name.lower().replace(' ', '_')}",
            row=row
        )
        self.role_id = role_id
        self.role_name = role_name
        
    async def callback(self, interaction: discord.Interaction):
        try:
            perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
            if not perco_channel:
                return await interaction.response.send_message("❌ Salon introuvable.", ephemeral=True)

            role_mention = f"<@&{self.role_id}>"
            user_display_name = interaction.user.display_name
            
            await perco_channel.send(
                content=f"{role_mention} **Votre percepteur est attaqué !** (Pingé par **{user_display_name}**)",
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            await interaction.response.send_message(f"✅ Alerte envoyée pour **{self.role_name}** !", ephemeral=True)
            
        except Exception as e:
            print(f"🛑 Erreur lors du clic : {e}")

# --- 2. CLASSE VIEW ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        for role_key, data in ROLES_PING.items():
            self.add_item(PingButton(
                role_id=data["id"], 
                role_name=role_key, 
                label=data["label"], 
                emoji_btn=data["emoji"],
                row=data["row"]
            ))

# --- 3. ÉVÉNEMENTS ---
@bot.event
async def on_ready():
    print(f"✅ Bot Connecté : {bot.user}")
    await asyncio.sleep(2)
    try:
        bot.add_view(PingAttackView())
        await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées.")
    except Exception as e:
        print(f"❌ Erreur Sync : {e}")

# --- 4. COMMANDE SETUP ---
@bot.tree.command(name="setup_ping_button", description="Envoie le panneau d'alerte perco.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        setup_embed = discord.Embed(
            title="📢 Alerte Attaque Percepteur",
            description="Cliquez sur le bouton correspondant à votre guilde pour alerter vos membres.",
            color=discord.Color.red()
        )
        
        if SETUP_IMAGE_URL:
            setup_embed.set_image(url=SETUP_IMAGE_URL)
        
        await interaction.channel.send(embed=setup_embed, view=PingAttackView())
        await interaction.followup.send("✅ Panneau configuré avec succès !")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur : {e}")

# --- LANCEMENT ---
keep_alive()
try:
    bot.run(token)
except Exception as e:
    print(f"❌ Erreur fatale : {e}")
