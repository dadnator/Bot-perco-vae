import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- VOS CONSTANTES ---
token = os.environ['TOKEN_BOT_DISCORD']

# Salon OÙ LE PING SERA ENVOYÉ (Alerte)
PERCO_CHANNEL_ID = 1241543017358299208 
# Salon OÙ LE BOUTON SERA AFFICHÉ (Setup)
CONFIRM_CHANNEL_ID = 1241543162078695595 

ROLE_ID = 1219962903260696596
TARGET_GUILD_ID = 1213932847518187561

target_guild = discord.Object(id=TARGET_GUILD_ID)

# Configuration du bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


# --- 1. CLASSE POUR LE BOUTON INTERACTIF (VIEW) ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        # S'assure que l'ID du bouton est permanent pour l'ajout après redémarrage
        self.ping_button.custom_id = "ping_atk_button_v1"

    @discord.ui.button(
        label="🚨 PING PERCEPTEUR",
        style=discord.ButtonStyle.red,
        emoji="⚔️"
    )
    async def ping_button(self, interaction: discord.Interaction, button: Button):
        # Répond immédiatement pour éviter le timeout
        await interaction.response.defer(ephemeral=True)
        
        # Récupération des salons et de la mention de rôle
        perco_channel = bot.get_channel(PERCO_CHANNEL_ID)
        
        if perco_channel:
            # --- MESSAGE D'ALERTE SIMPLIFIÉ ---
            alert_message_content = (
                f"{role_mention} "  # Mention du rôle
                "**Votre percepteur est attaqué ! 😡 PING ATK**"
            )
            
            # Envoi du message d'alerte dans le salon PERCO_CHANNEL
            await perco_channel.send(
                content=alert_message_content,
                # Autorise la mention de rôles
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            # Envoi du remerciement (Optionnel)
            if thanks_channel:
                 await thanks_channel.send(f"Merci à {interaction.user.mention} d'avoir déclenché l'alerte rapide 🫂")

            # Réponse éphémère à l'utilisateur
            await interaction.followup.send("✅ Alerte PING ATK envoyée ! GO DEF !", ephemeral=True)
        else:
            await interaction.followup.send("❌ Le salon d'alerte est introuvable. Veuillez vérifier PERCO_CHANNEL_ID.", ephemeral=True)


# --- 2. ÉVÉNEMENTS DU BOT ---

@bot.event
async def on_ready():
    """Se déclenche lorsque le bot est prêt."""
    print(f"✅ Connecté en tant que {bot.user}")
    
    try:
        # Ajout de la View persistante
        bot.add_view(PingAttackView())
        
        # Synchronisation des commandes slash
        bot.tree.clear_commands(guild=None) 
        await bot.tree.sync() 
        synced = await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées pour le serveur cible ({len(synced)} commande(s))")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation ou de l'ajout de la View : {e}")


# --- 3. COMMANDE POUR LE SETUP (création du message permanent) ---

@bot.tree.command(name="setup_ping_button", description="Envoie l'embed permanent avec le bouton d'alerte.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    """
    Envoie le message qui contient le bouton d'alerte dans le salon où cette commande est tapée.
    """
    await interaction.response.defer(ephemeral=True)

    # Création de l'embed pour le panneau de contrôle
    setup_embed = discord.Embed(
        title="📢 Panneau de Contrôle ATK Rapide",
        description="**CLIQUEZ UNE FOIS** sur le bouton ci-dessous pour envoyer un ping unique d'alerte Percepteur.",
        color=discord.Color.blue()
    )
    setup_embed.set_footer(text="Ce message est permanent. Ne le supprimez pas.")
    
    try:
        # Envoi du message permanent avec la View (le bouton)
        await interaction.channel.send(
            embed=setup_embed, 
            view=PingAttackView()
        )
        
        await interaction.followup.send("✅ Panneau de contrôle du bouton d'alerte envoyé dans ce salon.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur lors de l'envoi du message : {e}", ephemeral=True)


# --- LANCEMENT DU BOT ---
# keep_alive() # Optionnel
bot.run(token)
