from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="pay", description="Transfers money to a member.")
@app_commands.describe(
    recipient="The member to whom money will be transferred",
    amount="The amount of money"
)
async def pay(interaction: discord.Interaction, recipient: discord.Member, amount: int):
    guild_id = str(interaction.guild.id)
    author = interaction.user

    if amount <= 0:
        embed = discord.Embed(
            description=f"{emoji_error} The amount must be a positive integer.",
            color=color_error
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    sender_id = str(author.id)
    recipient_id = str(recipient.id)

    sender_data = money_collection.find_one({"guild_id": guild_id, "user_id": sender_id})
    recipient_data = money_collection.find_one({"guild_id": guild_id, "user_id": recipient_id})

    if not sender_data:
        embed = discord.Embed(
            description=f"{emoji_error} You don't have enough money. You currently have no money.",
            color=color_error
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    sender_cash = sender_data.get("cash", 0)

    if sender_cash >= amount:
        sender_cash -= amount

        money_collection.update_one({"guild_id": guild_id, "user_id": sender_id}, {"$set": {"cash": sender_cash}})

        if recipient_data:
            recipient_cash = recipient_data.get("cash", 0)
            recipient_cash += amount
            money_collection.update_one({"guild_id": guild_id, "user_id": recipient_id},
                                        {"$set": {"cash": recipient_cash}})
        else:
            money_collection.insert_one(
                {"guild_id": guild_id, "user_id": recipient_id, "cash": amount, "last_collect": None})

        embed = discord.Embed(
            description=f"{emoji_success} You have transferred {format_money(amount)} to {recipient.mention}.",
            color=color_success
        )
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=False)

    else:
        embed = discord.Embed(
            description=f"{emoji_error} You don't have enough money. You currently have {format_money(sender_cash)} in cash.",
            color=color_error
        )
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@pay.error
async def pay_error(interaction: discord.Interaction, error):
    embed = discord.Embed(color=color_error)

    if isinstance(error, commands.BadArgument):
        embed.description = f"{emoji_error} Invalid argument provided.\n\nUsage:\n``/pay <member> <amount>``"
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed.description = f"{emoji_error} An error occurred."
        await interaction.response.send_message(embed=embed, ephemeral=False)
