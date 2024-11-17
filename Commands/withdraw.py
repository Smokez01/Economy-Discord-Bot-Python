from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="withdraw", description="Withdraws money from the bank.")
@app_commands.describe(amount="The amount of money to withdraw. Use 'all' to withdraw your entire bank balance.")
async def withdraw(interaction: discord.Interaction, amount: str):
    guild_id = str(interaction.guild.id)
    user_id = str(interaction.user.id)
    existing_user = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if not existing_user:
        embed = discord.Embed(
            description=f"{emoji_error} You are not registered in the database.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    bank_balance = existing_user.get("bank", 0)

    if amount.lower() == "all":
        amount_to_withdraw = bank_balance
    else:
        try:
            amount_to_withdraw = int(amount)
            if amount_to_withdraw <= 0:
                embed = discord.Embed(
                    description=f"{emoji_error} Please enter a positive amount to withdraw.",
                    color=color_error
                )
                embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        except ValueError:
            embed = discord.Embed(
                description=f"{emoji_error} Please enter a valid amount or use 'all' to withdraw your entire bank balance.",
                color=color_error
            )
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    if amount_to_withdraw <= bank_balance:
        money_collection.update_one({"guild_id": guild_id, "user_id": user_id},
                                    {"$inc": {"bank": -amount_to_withdraw, "cash": amount_to_withdraw}})
        embed = discord.Embed(
            description=f"{emoji_success} You have withdrawn {emoji_money} {format_money(amount_to_withdraw)} from the bank.",
            color=color_success
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    else:
        embed = discord.Embed(
            description=f"{emoji_error} You do not have enough money in the bank to withdraw this amount.",
            color=color_error
        )
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
