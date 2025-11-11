import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, Button
from keep_alive import keep_alive
import asyncio

# --- VOS CONSTANTES (Gardées) ---
token = os.environ['TOKEN_BOT_DISCORD']

PERCO_CHANNEL_ID = 1241543017358299208 
CONFIRM_CHANNEL_ID = 1241543162078695595 

# ID du rôle principal (pour l'exemple initial, on peut le réutiliser ou le supprimer)
# ROLE_ID = 1219962903260696596 # Non utilisé directement dans la nouvelle structure
TARGET_GUILD_ID = 1213932847518187561

target_guild = discord.Object(id=TARGET_GUILD_ID)

# --- NOUVEAUX IDs DE RÔLES POUR LES 9 BOUTONS ---
# REMPLACER LES NUMÉROS (IDs) ET LES NOMS DES RÔLES
ROLES_PING = {
    "Coca": {"id": 121000000000000001, "label": "PING Rôle A"},
    "Skypeia": {"id": 121000000000000002, "label": "PING Rôle B"},
    "Origami": {"id": 121000000000000003, "label": "PING Rôle C"},
    "Pase-Hyfic": {"id": 121000000000000004, "label": "PING Rôle D"},
    "Sleeping": {"id": 121000000000000005, "label": "PING Rôle E"},
    "Sinaloa": {"id": 121000000000000006, "label": "PING Rôle F"},
    "La Bande": {"id": 121000000000000007, "label": "PING Rôle G"},
    "Bro's": {"id": 121000000000000008, "label": "PING Rôle H"},
}


# Configuration du bot
intents = discord.Intents.default()
# Nécessaire pour les interactions par boutons persistants
bot = commands.Bot(command_prefix="/", intents=intents)


# --- 2. CLASSE POUR LE BOUTON INTERACTIF (VIEW) ---
class PingAttackView(View):
    def __init__(self):
        # timeout=None est crucial pour que les boutons fonctionnent après le redémarrage du bot.
        super().__init__(timeout=None)
        
        # Création dynamique des 9 boutons
        for role_key, role_data in ROLES_PING.items():
            self.add_item(
                PingButton(
                    role_id=role_data["id"],
                    role_name=role_key,
                    label=role_data["label"]
                )
            )

# --- 3. CLASSE DU BOUTON INDIVIDUEL (pour réutiliser le code) ---
class PingButton(Button):
    def __init__(self, role_id: int, role_name: str, label: str):
        super().__init__(
            label=label,
            style=discord.ButtonStyle.red,
            emoji="⚔️",
            # Le custom_id est utilisé par Discord pour relier l'action du bouton à cette classe
            custom_id=f"ping_button_{role_name.lower().replace(' ', '_')}" 
        )
        self.role_id = role_id
        self.role_name = role_name
        
    async def callback(self, interaction: discord.Interaction):
        # Répond immédiatement pour éviter le timeout
        await interaction.response.defer(ephemeral=True)
        
        perco_channel = interaction.client.get_channel(PERCO_CHANNEL_ID)
        role_mention = f"<@&{self.role_id}>"
        
        if perco_channel:
            # --- MESSAGE D'ALERTE SIMPLIFIÉ ---
            alert_message_content = (
                f"{role_mention} "  # Mention du rôle ciblé
                f"**Votre percepteur est attaqué ! 😡 PING ATK ({self.role_name})**"
            )
            
            # Envoi du message d'alerte dans le salon PERCO_CHANNEL
            await perco_channel.send(
                content=alert_message_content,
                allowed_mentions=discord.AllowedMentions(roles=True) 
            )
            
            # Réponse éphémère à l'utilisateur
            await interaction.followup.send(
                f"✅ Alerte PING ATK envoyée pour le rôle **{self.role_name}** ! GO DEF !", 
                ephemeral=True
            )
        else:
            await interaction.followup.send("❌ Le salon d'alerte est introuvable. Veuillez vérifier PERCO_CHANNEL_ID.", ephemeral=True)


# --- 4. ÉVÉNEMENTS DU BOT (Restent les mêmes) ---

@bot.event
async def on_ready():
    """Se déclenche lorsque le bot est prêt."""
    print(f"✅ Connecté en tant que {bot.user}")
    
    try:
        # Ajout de la View persistante
        # IMPORTANT : Il faut ajouter la View principale (PingAttackView)
        bot.add_view(PingAttackView())
        
        # Synchronisation des commandes slash
        bot.tree.clear_commands(guild=None) 
        await bot.tree.sync() 
        synced = await bot.tree.sync(guild=target_guild) 
        print(f"✅ Commandes slash synchronisées pour le serveur cible ({len(synced)} commande(s))")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation ou de l'ajout de la View : {e}")


# --- 5. COMMANDE POUR LE SETUP (création du message permanent) ---

@bot.tree.command(name="setup_ping_button", description="Envoie l'embed permanent avec les 9 boutons d'alerte.", guild=target_guild)
@app_commands.default_permissions(administrator=True) 
async def setup_ping_button(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # Création de l'embed pour le panneau de contrôle
    setup_embed = discord.Embed(
        title="📢 Panneau de Contrôle ATK Rapide",
        description="**CLIQUEZ UNE FOIS** sur le bouton correspondant au rôle souhaité pour envoyer un ping unique d'alerte Percepteur.",
        color=discord.Color.blue()
    )
    setup_embed.set_footer(text="Ce message est permanent. Ne le supprimez pas.")
    
    try:
        # Envoi du message permanent avec la View (les 9 boutons)
        await interaction.channel.send(
            embed=setup_embed, 
            view=PingAttackView()
        )
        
        await interaction.followup.send("✅ Panneau de contrôle des 9 boutons d'alerte envoyé dans ce salon.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur lors de l'envoi du message : {e}", ephemeral=True)


# --- LANCEMENT DU BOT ---
keep_alive() # Optionnel
bot.run(token)
