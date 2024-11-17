from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="add-money", description="Adds money to a member.")
@app_commands.describe(
    member="The member to whom money will be added",
    amount="The amount of money",
    account_type="The account type (cash or bank)"
)
@app_commands.choices(account_type=[
    app_commands.Choice(name="Cash", value="cash"),
    app_commands.Choice(name="Bank", value="bank")
])
async def add_money(interaction: discord.Interaction, member: discord.Member, amount: int,
                    account_type: app_commands.Choice[str]):
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            description=f"{emoji_error} You do not have the required permissions to execute this command.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        return

    if amount <= 0:
        embed = discord.Embed(
            description=f"{emoji_error} The amount must be a positive integer.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)
        return

    guild_id = str(interaction.guild.id)
    user_id = str(member.id)  # Save user ID
    user_data = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if not user_data:
        money_collection.insert_one({"guild_id": guild_id, "user_id": user_id, "cash": 0, "bank": 0})

    money_collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$inc": {account_type.value: amount}})

    embed = discord.Embed(
        description=f"{emoji_success} {member.mention} has been given {emoji_money} {format_money(amount)} to the {account_type.value}.",
        color=color_success
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@add_money.error
async def add_money_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        embed = discord.Embed(
            description=f"{emoji_error} You do not have the required permissions to execute this command.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    elif isinstance(error, app_commands.errors.TransformerError):
        embed = discord.Embed(
            description=f"{emoji_error} Invalid argument provided.\n\nUsage:\n``/add_money <member> <amount> <account_type>``",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            description=f"{emoji_error} An error occurred.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
