from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="deposit", description="Deposits money to the bank.")
@app_commands.describe(amount="The amount of money to deposit. Use 'all' to deposit all your available money.")
async def deposit(interaction: discord.Interaction, amount: str):
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)

    user_data = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if not user_data:
        embed = discord.Embed(
            description=f"{emoji_error} Du hast kein Geld zum Einzahlen.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if amount.lower() == "all":
        amount_to_deposit = user_data["cash"]
    else:
        if not amount.isdigit():
            embed = discord.Embed(
                description=f"{emoji_error} Bitte gib einen gültigen Betrag ein, den du einzahlen möchtest.",
                color=color_error
            )
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        amount_to_deposit = int(amount)

        if amount_to_deposit <= 0:
            embed = discord.Embed(
                description=f"{emoji_error} Bitte gib einen positiven Betrag ein, den du einzahlen möchtest.",
                color=color_error
            )
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if amount_to_deposit > user_data["cash"]:
            embed = discord.Embed(
                description=f"{emoji_error} Du hast nicht genug Geld, um diesen Betrag einzuzahlen.",
                color=color_error
            )
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    # Update auch hier "name" auf "user_id" ändern
    money_collection.update_one({"guild_id": guild_id, "user_id": user_id},
                                {"$inc": {"cash": -amount_to_deposit, "bank": amount_to_deposit}})

    embed = discord.Embed(
        description=f"{emoji_success} Du hast {emoji_money} {format_money(amount_to_deposit)} in die Bank eingezahlt.",
        color=color_success
    )
    embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)
