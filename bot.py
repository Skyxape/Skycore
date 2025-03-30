import discord
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from keep_alive import keep_alive
load_dotenv()

print("Lancement du bot...")
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot alumé !")
    #synchroniser les commandes
    try:
        #sync
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(e)

@bot.tree.command(name="server_stats", description="Obtenir des statistiques sur le serveur")
async def server_stats(interaction: discord.Interaction):
    guild = interaction.guild

    # Récupérer les informations demandées
    total_members = guild.member_count
    online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
    voice_members = sum(1 for member in guild.members if member.voice)
    streaming_members = sum(1 for member in guild.members if member.activity and isinstance(member.activity, discord.Streaming))

    # Créer l'embed avec les informations du serveur
    embed = discord.Embed(
        title=f"{guild.name} Stats",
        description=f"Voici les statistiques du serveur **{guild.name}**",
        color=discord.Color.blue()
    )
    embed.add_field(name="Nombre total de membres", value=total_members, inline=False)
    embed.add_field(name="Membres en ligne", value=online_members, inline=False)
    embed.add_field(name="Membres en vocal", value=voice_members, inline=False)
    embed.add_field(name="Membres en stream", value=streaming_members, inline=False)
    
    # Ajouter l'icône du serveur en image
    embed.set_thumbnail(url=guild.icon.url)

    # Envoyer l'embed
    await interaction.response.send_message(embed=embed)
    print("Stats du serveur envoyées")


@bot.tree.command(name="ping", description="Vérifier la latence du bot")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! Latence : {round(bot.latency * 1000)}ms")
    print(f"Latence du bot {round(bot.latency * 1000)}ms")

@bot.tree.command(name="add_role", description="Ajouter un rôle à un membre")
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    # Vérification des permissions
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("Tu n'as pas la permission de gérer les rôles.", ephemeral=True)
        return
    
    # Vérification si le rôle est plus élevé que celui du bot
    if role.position >= interaction.guild.me.top_role.position:
        await interaction.response.send_message("Je ne peux pas attribuer ce rôle, il est plus élevé que mon rôle.", ephemeral=True)
        return

    # Ajouter le rôle au membre
    try:
        await member.add_roles(role)
        await interaction.response.send_message(f"Le rôle {role.name} a été ajouté à {member.mention}.")
        print(f"Rôle {role.name} attribué à {member.mention}")
    except discord.DiscordException as e:
        await interaction.response.send_message(f"Une erreur est survenue : {str(e)}", ephemeral=True)
        print(f"Erreur lors de l'attibution du rôle {role.name} à {member.mention}")

@bot.event
async def on_message(message: discord.Message):
    #empêcher le bot de se déclencher lui même
    if message.author.bot:
        return

    if message.content.lower() == 'bonjour':
        channel = message.channel
        author = message.author
        await author.send("Comment tu vas ?")
    if message.content.lower() == "bienvenue":
        welcome_channel = bot.get_channel(1353797438888218736)
        await welcome_channel.send("Bienvenue")

@bot.tree.command(name="charte", description="Affiche le chartre du serveur")
async def charte(interaction: discord.Interaction):
    charte_channel = bot.get_channel(1354520537375965184)
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return
    embed = discord.Embed(title="📜 Charte du Serveur Discord 📜", color=discord.Color.yellow())
    embed.add_field(name="1. Respect et Bienveillance", value="✅ Soyez respectueux envers tous les membres. Aucune insulte, harcèlement, menace ou discrimination ne sera tolérée. \n"
    "❌ Pas d’insultes, harcèlement, discrimination ou provocation.\n", inline=False)
    embed.add_field(name="2. Contenu Autorisé et Interdit", value="✅ Partagez uniquement du contenu approprié et légal.\n"
    "❌ Aucune publication de contenu NSFW (pornographique, gore, violent, etc...) ou autre contenu illégal, piratage.\n", inline=False)
    embed.add_field(name="3. Canaux et Bon Usage", value="✅ Postez dans les bons canaux.\n"
    "❌ Pas de spam, flood ou hors-sujet.\n", inline=False)
    embed.add_field(name="4. Publicité et Spam", value="❌ Pas de pub sauvage ou de spam.\n", inline=False)
    embed.add_field(name="5. Sécurité", value="✅ Ne partagez pas d’infos personnelles.\n"
    "❌ Pas d’arnaque, phishing ou usurpation d’identité.", inline=False)
    await charte_channel.send(embed=embed)
    await interaction.response.send_message("Charte envoyée dans le channel", ephemeral=True)
    print("Charte envoyée dans le channel")

@bot.tree.command(name="clear", description="Supprimer plusieurs messages")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Tu n'as pas la permission de gérer les messages.", ephemeral=True)
        return

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"{amount} message(s) supprimé(s).", ephemeral=True)
    print(f"{amount} message(s) supprimé(s)")


@bot.tree.command(name="infos_user", description="Donne les infos d'un utilisateur")
async def infos_user(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    
    embed = discord.Embed(title=f"Informations sur {member.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Nom d'affichage", value=member.display_name, inline=False)
    embed.add_field(name="Compte créé le", value=member.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="A rejoint le serveur le", value=member.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.set_footer(text=f"Demandé par {interaction.user.name}")
    
    await interaction.response.send_message(embed=embed)
    print(f"Les infos du membre {member} ont étés envoyées")

@bot.tree.command(name="server_info", description="Obtenir des informations sur le serveur")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"Informations sur le serveur {guild.name}", color=discord.Color.green())
    embed.add_field(name="ID", value=guild.id, inline=False)
    embed.add_field(name="Propriétaire", value=guild.owner, inline=False)
    embed.add_field(name="Nombre de membres", value=guild.member_count, inline=False)
    embed.add_field(name="Nombre de rôles", value=len(guild.roles), inline=False)
    embed.add_field(name="Date de création", value=guild.created_at.strftime("%d/%m/%Y %H:%M"), inline=False)
    embed.set_thumbnail(url=guild.icon.url)
    await interaction.response.send_message(embed=embed)
    print(f"Les infos du serveur ont été envoyées")


@bot.tree.command(name="warn", description="Alerter une personne")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return
    await interaction.response.send_message(f"Alerte envoyée à {member.mention} ! Raison : {reason}", ephemeral=True)
    await member.send(f"Tu as reçu une alerte ! Raison : {reason}")
    print(f"{member} a été averti pour {reason}")


@bot.tree.command(name="ban", description="Bannir une personne")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return
    await interaction.response.send_message(f"Bannissement de {member.mention} effectué ! Raison : {reason}", ephemeral=True)
    await member.ban(reason=reason)
    try:
        await member.send(f"Tu as été banni du serveur ! Raison : {reason}")
    except discord.Forbidden:
        # Si le bot ne peut pas envoyer de message privé, il avertit l'administrateur
        await interaction.followup.send(f"Impossible d'envoyer un message privé à {member.mention}, il/elle a probablement désactivé les messages privés.")
    print(f"{member} a été banni pour la raison suivante : {reason}")

@bot.tree.command(name="kick", description="Expulser une personne")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return
    await interaction.response.send_message(f"Expulsion de {member.mention} effectuée ! Raison : {reason}", ephemeral=True)
    await member.kick(reason=reason)
    try:
        await member.send(f"Tu as été expulsé du serveur ! Raison : {reason}")
    except discord.Forbidden:
        # Si le bot ne peut pas envoyer de message privé, il avertit l'administrateur
        await interaction.followup.send(f"Impossible d'envoyer un message privé à {member.mention}, il/elle a probablement désactivé les messages privés.")
    print(f"{member} a été expulsé pour la raison suivante : {reason}")


@bot.tree.command(name="mute", description="Muter un utilisateur")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int, reason: str):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("Tu n'as pas la permission de muter des membres.", ephemeral=True)
        return

    # Trouver ou créer le rôle "Muted"
    mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await interaction.guild.create_role(name="Muted", reason="Rôle pour les membres muets")
        print(f"Rôle Muted créé")

    # Ajouter le rôle "Muted" au membre
    await member.add_roles(mute_role, reason=reason)
    print(f"Rôle Muted ajouté à {member}")
    
    # Envoyer un message de confirmation dans le chat
    await interaction.response.send_message(f"{member.mention} a été réduit au silence pour {duration} minutes. Raison : {reason}")
    print(f"{member} a été réduit au silence pour {duration} minutes. Raison : {reason}")

    # Délai pour enlever le mute
    await asyncio.sleep(duration * 60)
    await member.remove_roles(mute_role, reason="Fin de la durée du mute.")
    print(f"Fin de la durée du mute pour {member}")
    await interaction.channel.send(f"{member.mention} n'est plus mute.")
    print(f"{member} n'est plus réduit au silence")

#créer un rôle
@bot.tree.command(name="create_role", description="Crée un rôle avec un nom et une couleur spécifiée.")
async def create_role(interaction: discord.Interaction, role_name: str, hex_color: str = "#FFFFFF"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return
    
    try:
        color = discord.Color(int(hex_color.lstrip("#"), 16))
        

        guild = interaction.guild
        role = await guild.create_role(name=role_name, color=color)
        
        await interaction.response.send_message(f'Rôle `{role_name}` créé avec succès !', ephemeral=True)
        print(f"Rôle {role_name} créé avec succès !")
    except Exception as e:
        await interaction.response.send_message(f'Erreur lors de la création du rôle: {e}', ephemeral=True)
        print(f"Erreur lors de la création du rôle {role_name} : {e}")

# supprimer un rôle
@bot.tree.command(name="delete_role", description="Supprime un rôle existant.")
async def delete_role(interaction: discord.Interaction, role_name: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Vous devez être administrateur pour utiliser cette commande.", ephemeral=True)
        return
    
    try:
        guild = interaction.guild
        role = discord.utils.get(guild.roles, name=role_name)
        
        if role:
            await role.delete()
            await interaction.response.send_message(f'Rôle `{role_name}` supprimé avec succès!', ephemeral=True)
            print(f'Le rôle "{role_name}" a été supprimé.')
        else:
            await interaction.response.send_message(f'Le rôle `{role_name}` n\'existe pas.', ephemeral=True)
            print(f"Le rôle {role_name} n'existe pas.")
    except Exception as e:
        await interaction.response.send_message(f'Erreur lors de la suppression du rôle: {e}', ephemeral=True)
        print(f"Erreur lors de la suppression du rôle: {e}")

# Commande pour créer une catégorie
@bot.tree.command(name="create_category", description="Créer une nouvelle catégorie")
async def create_category(interaction: discord.Interaction, category_name: str):
    # Vérification des permissions
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Tu n'as pas la permission de gérer les canaux.", ephemeral=True)
        return
    
    # Créer la catégorie
    try:
        category = await interaction.guild.create_category(category_name)
        await interaction.response.send_message(f"La catégorie '{category_name}' a été créée avec succès !")
        print(f"La catégorie '{category_name}' a été créée avec succès !")
    except discord.DiscordException as e:
        await interaction.response.send_message(f"Une erreur est survenue : {str(e)}", ephemeral=True)
        print(f"Une erreur est survenue : {str(e)} lors de la création de la catégorie {category_name}")

# Commande pour créer un channel dans une catégorie
@bot.tree.command(name="create_text_channel", description="Créer un nouveau channel dans une catégorie")
async def create_text_channel(interaction: discord.Interaction, channel_name: str):
    # Vérification des permissions
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Tu n'as pas la permission de gérer les canaux.", ephemeral=True)
        return
    
    # Récupérer les catégories existantes
    categories = [category for category in interaction.guild.categories]
    
    # Si aucune catégorie n'existe, envoyer un message d'erreur
    if not categories:
        await interaction.response.send_message("Aucune catégorie disponible dans ce serveur.", ephemeral=True)
        return
    
    # Créer un menu déroulant pour choisir la catégorie
    options = [discord.SelectOption(label=category.name, value=str(category.id)) for category in categories]
    
    # Créer un SelectMenu (menu déroulant) pour choisir une catégorie
    select = discord.ui.Select(placeholder="Choisis une catégorie", options=options)

    # Fonction appelée lorsque l'utilisateur choisit une catégorie
    async def select_callback(interaction: discord.Interaction):
        # Récupérer la catégorie sélectionnée
        selected_category_id = int(select.values[0])
        selected_category = discord.utils.get(interaction.guild.categories, id=selected_category_id)

        # Créer le channel dans la catégorie sélectionnée
        try:
            await interaction.guild.create_text_channel(channel_name, category=selected_category)
            await interaction.response.send_message(f"Le channel {channel_name} a été créé dans la catégorie {selected_category.name} !")
            print(f"Le channel {channel_name} a été créé dans la catégorie {selected_category.name} !")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Une erreur est survenue : {str(e)}", ephemeral=True)
            print(f"Une erreur est survenue lors de la création du channel {channel_name} dans {selected_category.name} : {str(e)}")

    # Ajouter un bouton pour envoyer la réponse
    select.callback = select_callback

    # Créer une vue avec le SelectMenu
    view = discord.ui.View()
    view.add_item(select)

    # Envoyer un message pour demander de choisir la catégorie
    await interaction.response.send_message("Choisis une catégorie dans laquelle créer le channel.", view=view)

# Commande pour créer un channel vocal dans une catégorie
@bot.tree.command(name="create_voice_channel", description="Créer un nouveau channel vocal dans une catégorie")
async def create_voice_channel(interaction: discord.Interaction, channel_name: str):
    # Vérification des permissions
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Tu n'as pas la permission de gérer les canaux.", ephemeral=True)
        return
    
    # Récupérer les catégories existantes
    categories = [category for category in interaction.guild.categories]
    
    # Si aucune catégorie n'existe, envoyer un message d'erreur
    if not categories:
        await interaction.response.send_message("Aucune catégorie disponible dans ce serveur.", ephemeral=True)
        return
    
    # Créer un menu déroulant pour choisir la catégorie
    options = [discord.SelectOption(label=category.name, value=str(category.id)) for category in categories]
    
    # Créer un SelectMenu (menu déroulant) pour choisir une catégorie
    select = discord.ui.Select(placeholder="Choisis une catégorie", options=options)

    # Fonction appelée lorsque l'utilisateur choisit une catégorie
    async def select_callback(interaction: discord.Interaction):
        # Récupérer la catégorie sélectionnée
        selected_category_id = int(select.values[0])
        selected_category = discord.utils.get(interaction.guild.categories, id=selected_category_id)

        # Créer le channel vocal dans la catégorie sélectionnée
        try:
            await interaction.guild.create_voice_channel(channel_name, category=selected_category)
            await interaction.response.send_message(f"Le channel vocal {channel_name} a été créé dans la catégorie {selected_category.name} !")
            print(f"Le channel vocal {channel_name} a été créé dans la catégorie {selected_category.name} !")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Une erreur est survenue : {str(e)}", ephemeral=True)
            print(f"Une erreur est survenue lors de la création de {channel_name} dans {selected_category} : {str(e)}")

    # Ajouter un bouton pour envoyer la réponse
    select.callback = select_callback

    # Créer une vue avec le SelectMenu
    view = discord.ui.View()
    view.add_item(select)

    # Envoyer un message pour demander de choisir la catégorie
    await interaction.response.send_message("Choisis une catégorie dans laquelle créer le channel vocal.", view=view)

# Commande pour créer un channel de conférence dans une catégorie
@bot.tree.command(name="create_conference_channel", description="Créer un channel de conférence dans une catégorie")
async def create_conference_channel(interaction: discord.Interaction, channel_name: str):
    # Vérification des permissions
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("Tu n'as pas la permission de gérer les canaux.", ephemeral=True)
        return
    
    # Récupérer les catégories existantes
    categories = [category for category in interaction.guild.categories]
    
    # Si aucune catégorie n'existe, envoyer un message d'erreur
    if not categories:
        await interaction.response.send_message("Aucune catégorie disponible dans ce serveur.", ephemeral=True)
        return
    
    # Créer un menu déroulant pour choisir la catégorie
    options = [discord.SelectOption(label=category.name, value=str(category.id)) for category in categories]
    
    # Créer un SelectMenu (menu déroulant) pour choisir une catégorie
    select = discord.ui.Select(placeholder="Choisis une catégorie", options=options)

    # Fonction appelée lorsque l'utilisateur choisit une catégorie
    async def select_callback(interaction: discord.Interaction):
        # Récupérer la catégorie sélectionnée
        selected_category_id = int(select.values[0])
        selected_category = discord.utils.get(interaction.guild.categories, id=selected_category_id)

        # Créer le channel vocal de conférence dans la catégorie sélectionnée
        try:
            # Créer un channel vocal avec des options adaptées aux conférences (par exemple, nombre de personnes limitées)
            await interaction.guild.create_voice_channel(
                channel_name,
                category=selected_category,
                user_limit=25,  # Limite des utilisateurs, exemple pour une conférence
                reason="Création d'un channel de conférence"
            )
            await interaction.response.send_message(f"Le channel de conférence {channel_name} a été créé dans la catégorie {selected_category.name} !")
            print(f"Le channel de conférence {channel_name} a été créé dans la catégorie {selected_category.name} !")
        except discord.DiscordException as e:
            await interaction.response.send_message(f"Une erreur est survenue : {str(e)}", ephemeral=True)
            print(f"Une erreur est survenue lors de la création de {channel_name} dans {selected_category} : {str(e)}")

    # Ajouter un bouton pour envoyer la réponse
    select.callback = select_callback

    # Créer une vue avec le SelectMenu
    view = discord.ui.View()
    view.add_item(select)

    # Envoyer un message pour demander de choisir la catégorie
    await interaction.response.send_message("Choisis une catégorie dans laquelle créer le channel de conférence.", view=view)

keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))