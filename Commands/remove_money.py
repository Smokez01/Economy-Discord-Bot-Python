from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="remove-money", description="Removes money from a member.")
@app_commands.describe(
    member="The member from whom money will be removed",
    amount="The amount of money",
    account_type="The account type (cash or bank)"
)
@app_commands.choices(account_type=[
    app_commands.Choice(name="Cash", value="cash"),
    app_commands.Choice(name="Bank", value="bank")
])
async def remove_money(interaction: discord.Interaction, member: discord.Member, amount: int,
                       account_type: app_commands.Choice[str]):
    guild_id = str(interaction.guild.id)
    author = interaction.user

    if not author.guild_permissions.administrator:
        embed = discord.Embed(
            description=f"{emoji_error} You don't have the required permissions to execute this command.",
            color=color_error
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if amount <= 0:
        embed = discord.Embed(
            description=f"{emoji_error} The amount must be a positive integer.",
            color=color_error
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    user_id = str(member.id)
    existing_user = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if not existing_user:
        money_collection.insert_one({"guild_id": guild_id, "user_id": user_id, "cash": 0, "bank": 0})
        existing_user = {"guild_id": guild_id, "user_id": user_id, "cash": 0, "bank": 0}

    user_funds = existing_user.get(account_type.value, 0)
    if user_funds >= amount:
        money_collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {account_type.value: -amount}})
        embed = discord.Embed(
            description=f"{emoji_success} {member.mention} has had {emoji_money} {format_money(amount)} removed from their {account_type.value}.",
            color=color_success
        )
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    else:
        money_collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {account_type.value: -amount}})
        embed = discord.Embed(
            description=f"{emoji_success} {member.mention} didn't have enough money in their {account_type.value}. However, {emoji_money} {format_money(amount)} was still removed.",
            color=color_success
        )
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=False)

        await log_money_transaction(
            guild_id,
            f"{author.mention} removed {emoji_money} {format_money(amount)} from {member.mention}'s {account_type.value} despite insufficient funds.",
            author.name,
            str(author.avatar.url)
        )

@remove_money.error
async def remove_money_error(interaction: discord.Interaction, error):
    embed = discord.Embed(color=color_error)

    if isinstance(error, app_commands.errors.MissingPermissions):
        embed.description = f"{emoji_error} You don't have the required permissions to execute this command."
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif isinstance(error, app_commands.errors.TransformerError):
        embed.description = f"{emoji_error} Invalid argument provided.\n\nUsage:\n``/remove-money <member> <amount> <account_type>``"
        await interaction.response.send_message(embed=embed, ephemeral=True)
