from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="money", description="Displays a member's money.")
@app_commands.describe(user="The member whose money should be displayed")
async def money(interaction: discord.Interaction, user: discord.Member = None):
    print(f"Command called by: {interaction.user.name}, with user: {user.name if user else 'None'}")

    if user is None:
        user = interaction.user

    if user != interaction.user:
        print(f"Checking permissions for: {interaction.user.name} to view {user.name}")
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(color=color_error)
            embed.description = f"{emoji_error} You do not have permission to view other members' money."
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

    user_data = money_collection.find_one({"guild_id": str(interaction.guild.id), "user_id": str(user.id)})
    print(f"User data for {user.name}: {user_data}")

    embed = discord.Embed(color=color_success)

    if user_data:
        cash = int(user_data.get("cash", 0))
        bank = int(user_data.get("bank", 0))
        total = cash + bank

        print(f"Cash: {cash}, Bank: {bank}, Total: {total}")

        embed.add_field(name=f"{emoji_money} Cash", value=f"{format_money(cash)}", inline=True)
        embed.add_field(name=f"{emoji_money} Bank", value=f"{format_money(bank)}", inline=True)
        embed.add_field(name=f"{emoji_money} Total", value=f"{format_money(total)}", inline=True)

        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url
        embed.set_author(name=user.name, icon_url=avatar_url)
    else:
        embed.color = color_error
        embed.description = f"{emoji_error} Member not found."

    await interaction.response.send_message(embed=embed, ephemeral=False)

@money.error
async def money_error(interaction: discord.Interaction, error):
    embed = discord.Embed(color=color_error)
    embed.description = f"{emoji_error} Invalid argument provided.\n\nUsage:\n``/money <member>``"

    print(f"Error occurred: {error}")

    if isinstance(error, commands.MemberNotFound):
        await interaction.response.send_message(embed=embed, ephemeral=False)
        error.handled = True
    elif isinstance(error, commands.BadArgument):
        await interaction.response.send_message(embed=embed, ephemeral=False)
        error.handled = True
    else:
        await interaction.response.send_message(embed=embed, ephemeral=False)
