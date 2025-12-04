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
CONFIRM_CHANNEL_ID = 1446104046300696598

TARGET_GUILD_ID = 1445883050163703904

target_guild = discord.Object(id=TARGET_GUILD_ID)

# --- URL DE L'IMAGE POUR L'EMBED DES BOUTONS ---
# ⚠️ REMPLACEZ CETTE CHAÎNE par l'URL publique de votre image.
SETUP_IMAGE_URL = "https://i.imgur.com/8setyQq.png" 


# --- IDs DE RÔLES, LABELS ET ÉMOJIS POUR LES 8 BOUTONS ---
ROLES_PING = {
    "Sleeping": {"id": 1446103551951638570, "label": " Sleeping", "emoji": "<:TheSleepingBlossoms:1359180403155406878>"},
    "La Bande": {"id": 1446104186533056684, "label": " La Bande", "emoji": "<:LABANDE:1388101932886917222>"},
}


# Configuration du bot
intents = discord.Intents.default()
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
        await interaction.response.defer(ephemeral=True)
        
        perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
        role_mention = f"<@&{self.role_id}>"

        # Récupération du nom d'affichage de l'utilisateur (username ou nickname s'il est dans la guilde)
        # On utilise interaction.user.display_name pour obtenir le nom le plus pertinent
        user_display_name = interaction.user.display_name
        
        if perco_channel:
            # MESSAGE D'ALERTE (simple, pas d'embed)
            alert_message_content = (
                f"{role_mention} "
                f"**Votre percepteur est attaqué !** (Pingé par **{user_display_name}**)" # <-- MODIFICATION ICI
            )
            
            # Envoi du message d'alerte dans le salon PERCO_CHANNEL
            await perco_channel.send(
                content=alert_message_content,
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            # Réponse éphémère à l'utilisateur
            await interaction.followup.send(
                f"✅ Alerte PING DEF envoyée pour le rôle **{self.role_name}** ! Merci pour le ping!", 
                ephemeral=True
            )
        else:
            await interaction.followup.send("❌ Le salon d'alerte est introuvable. Veuillez vérifier PERCO_CHANNEL_ID.", ephemeral=True)


# --- 2. CLASSE CONTENANT TOUS LES BOUTONS (VIEW) ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        for role_key, role_data in ROLES_PING.items():
            self.add_item(
                PingButton(
                    role_id=role_data["id"],
                    role_name=role_key,
                    label=role_data["label"],
                    emoji_btn=role_data["emoji"]
                )
            )


# --- 3. ÉVÉNEMENTS DU BOT ---
@bot.event
async def on_ready():
    """Se déclenche lorsque le bot est prêt."""
    print(f"✅ Bot Connecté en tant que {bot.user}")
    
    try:
        bot.add_view(PingAttackView())
        
        # Synchronisation des commandes slash
        bot.tree.clear_commands(guild=None) 
        await bot.tree.sync() 
        synced = await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées pour le serveur cible ({len(synced)} commande(s))")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation ou de l'ajout de la View : {e}")


# --- 4. COMMANDE POUR LE SETUP (création du message permanent) ---

@bot.tree.command(name="setup_ping_button", description="Envoie l'embed permanent avec les 8 boutons d'alerte.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # Création de l'embed pour le panneau de contrôle
    setup_embed = discord.Embed(
        title="📢 Un Perco Attaqué ",
        description="**CLIQUEZ UNE FOIS** sur le bouton correspondant au groupe souhaité pour envoyer un ping unique d'alerte Percepteur.",
        color=discord.Color.blue()
    )
    setup_embed.set_footer(text="Ce message est permanent. Ne le supprimez pas.")
    
    # --- AJOUT DE L'IMAGE À L'EMBED DE SETUP ---
    if SETUP_IMAGE_URL and SETUP_IMAGE_URL != "URL_DE_VOTRE_IMAGE_POUR_LE_PANNEAU_DE_BOUTONS_ICI":
        setup_embed.set_image(url=SETUP_IMAGE_URL)
    # ----------------------------------------
    
    try:
        # Envoi du message permanent avec la View (les 8 boutons)
        await interaction.channel.send(
            embed=setup_embed, 
            view=PingAttackView()
        )
        
        await interaction.followup.send("✅ Panneau de contrôle des 8 boutons d'alerte envoyé dans ce salon.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur lors de l'envoi du message : {e}", ephemeral=True)


# --- LANCEMENT DU BOT ---
keep_alive()
bot.run(token)
