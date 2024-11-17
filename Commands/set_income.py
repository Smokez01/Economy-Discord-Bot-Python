from datetime import timedelta
from Events.format_money import format_money
from client import *
from database import income_collection

@client.tree.command(name="set-income", description="Assigns income to a role.")
@app_commands.describe(role="The role to assign income to", amount="The income amount", cooldown="The cooldown period (in hours) for collecting the income.")
async def set_income(interaction: discord.Interaction, role: discord.Role, amount: int, cooldown: int):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            description=f"{emoji_error} You do not have the required permissions to execute this command.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        return

    guild_id = str(interaction.guild.id)
    role_mention = role.mention

    if amount < 0:
        embed = discord.Embed(
            description=f"{emoji_error} The amount must be a positive number.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        return

    if cooldown <= 0:
        embed = discord.Embed(
            description=f"{emoji_error} The cooldown period must be a positive number.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        return

    existing_role = income_collection.find_one({"guild_id": guild_id, "role_id": str(role.id)})

    if existing_role:
        income_collection.update_one(
            {"guild_id": guild_id, "role_id": str(role.id)},
            {"$set": {"amount": amount, "cooldown": cooldown}}
        )
    else:
        income_collection.insert_one({
            "guild_id": guild_id,
            "role_id": str(role.id),
            "amount": amount,
            "cooldown": cooldown
        })

    formatted_amount = format_money(amount)
    embed = discord.Embed(
        title="Income Updated",
        description=f"{emoji_success} Income for role {role_mention} has been set to {formatted_amount}.\nCooldown: {cooldown} hours.",
        color=color_success
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@set_income.error
async def set_income_error(interaction: discord.Interaction, error):
    embed = discord.Embed(color=color_error)
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)

    if isinstance(error, app_commands.errors.MissingRole):
        embed.description = f"{emoji_error} Invalid `<role>` argument provided.\n\nUsage:\n/set-income <role> <amount> <cooldown>"
    elif isinstance(error, app_commands.errors.MissingRequiredArgument):
        embed.description = f"{emoji_error} Too few arguments provided.\n\nUsage:\n`/set-income <role> <amount> <cooldown>`"
    else:
        embed.description = f"{emoji_error} An error occurred.\n\nUsage:\n/set-income <role> <amount> <cooldown>"

    await interaction.response.send_message(embed=embed, ephemeral=True)
