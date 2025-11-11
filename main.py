import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- VOS CONSTANTES (Gardées) ---
token = os.environ['TOKEN_BOT_DISCORD']

PERCO_CHANNEL_ID = 1366384335615164529 
CONFIRM_CHANNEL_ID = 1366384437503332464 

TARGET_GUILD_ID = 1366369136648654868

target_guild = discord.Object(id=TARGET_GUILD_ID)

# --- IDs DE RÔLES, LABELS ET ÉMOJIS POUR LES 8 BOUTONS ---
ROLES_PING = {
    "Coca": {"id": 1437803787061301308, "label": "PING Coca", "emoji": "<:coca:1337898909321793588>"},
    "Skypeia": {"id": 1437803979336843346, "label": "PING Skypeia", "emoji": "<:sky:1337898940963750010>"},
    "Origami": {"id": 1437804353531678863, "label": "PING Origami", "emoji": "<:ori:1337898349478805566>"},
    "Pase-Hyfic": {"id": 1437804605605019739, "label": "PING Pase-Hyfic", "emoji": "<:pase:1355031214033076326>"},
    "Sleeping": {"id": 1437803468474552462, "label": "PING Sleeping", "emoji": "<:TheSleepingBlossoms:1359180403155406878>"},
    "Sinaloa": {"id": 1437803888421113898, "label": "PING Sinaloa", "emoji": "<:SINALOA:1391477497618759720>"},
    "La Bande": {"id": 1437804134660050964, "label": "PING La Bande", "emoji": "<:LABANDE:1388101932886917222>"},
    "Bro's": {"id": 1437804247042494474, "label": "PING Bro's", "emoji": "<:Bros:1435705562066063491>"},
}


# Configuration du bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


# --- 1. CLASSE POUR LE BOUTON INDIVIDUEL ---
class PingButton(Button):
    # Ajout du paramètre 'emoji_btn' et style fixé à danger (rouge)
    def __init__(self, role_id: int, role_name: str, label: str, emoji_btn: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.danger,  # Style ROUGE fixe
            emoji=emoji_btn,                   # Utilise l'émoji unique
            custom_id=f"ping_button_{role_name.lower().replace(' ', '_')}" 
        )
        self.role_id = role_id
        self.role_name = role_name
        
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
        role_mention = f"<@&{self.role_id}>"
        
        if perco_channel:
            # --- MESSAGE D'ALERTE CORRIGÉ ET COMPLET ---
            alert_message_content = (
                f"{role_mention} "  # Mention du rôle ciblé
                f"**Votre percepteur est attaqué ! 😡 PING DEF ({self.role_name})**"
            )
            
            # Envoi du message d'alerte dans le salon PERCO_CHANNEL
            await perco_channel.send(
                content=alert_message_content,
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            # Réponse éphémère à l'utilisateur
            await interaction.followup.send(
                f"✅ Alerte PING DEF envoyée pour le rôle **{self.role_name}** ! GO DEF !", 
                ephemeral=True
            )
        else:
            await interaction.followup.send("❌ Le salon d'alerte est introuvable. Veuillez vérifier PERCO_CHANNEL_ID.", ephemeral=True)


# --- 2. CLASSE CONTENANT TOUS LES BOUTONS (VIEW) ---
class PingAttackView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Création dynamique des 8 boutons
        for role_key, role_data in ROLES_PING.items():
            self.add_item(
                PingButton(
                    role_id=role_data["id"],
                    role_name=role_key,
                    label=role_data["label"],
                    emoji_btn=role_data["emoji"]  # Passage de l'émoji
                )
            )


# --- 3. ÉVÉNEMENTS DU BOT ---
@bot.event
async def on_ready():
    """Se déclenche lorsque le bot est prêt."""
    print(f"✅ Bot Connecté en tant que {bot.user}")
    
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


# --- 4. COMMANDE POUR LE SETUP (création du message permanent) ---

@bot.tree.command(name="setup_ping_button", description="Envoie l'embed permanent avec les 8 boutons d'alerte.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # Création de l'embed pour le panneau de contrôle
    setup_embed = discord.Embed(
        title="📢 Panneau de Contrôle DEF Rapide (8 Groupes)",
        description="**CLIQUEZ UNE FOIS** sur le bouton correspondant au groupe souhaité pour envoyer un ping unique d'alerte Percepteur.",
        color=discord.Color.blue()
    )
    setup_embed.set_footer(text="Ce message est permanent. Ne le supprimez pas.")
    
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
