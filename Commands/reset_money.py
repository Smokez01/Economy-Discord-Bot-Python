from Events.format_money import format_money
from client import *
from database import money_collection

@client.tree.command(name="reset-money", description="Resets the money of a member.")
@app_commands.describe(
    member="The member whose money should be reset (optional, defaults to the command invoker)"
)
async def reset_money(interaction: discord.Interaction, member: discord.Member = None):
    guild_id = str(interaction.guild.id)
    author = interaction.user

    if not author.guild_permissions.administrator:
        embed = discord.Embed(
            description=f"{emoji_error} You don't have the required permissions to execute this command.",
            color=color_error
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    if member is None:
        member = author

    user_id = str(member.id)
    existing_user = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    if existing_user:
        total_reset_money = existing_user["cash"] + existing_user["bank"]
        money_collection.update_one({"guild_id": guild_id, "user_id": user_id}, {"$set": {"bank": 0, "cash": 0}})
        formatted_total_reset_money = format_money(total_reset_money)

        embed = discord.Embed(
            description=f"{emoji_success} {member.mention}'s money has been successfully reset!\nTotal money reset: {emoji_money} {formatted_total_reset_money}",
            color=color_success
        )
        embed.set_author(name=author.name, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=embed)

    else:
        embed_not_registered = discord.Embed(
            description=f"{emoji_error} {member.mention} is not registered in the money collection.",
            color=color_error
        )
        embed_not_registered.set_author(name=author.name, icon_url=author.avatar.url)
        await interaction.response.send_message(embed=embed_not_registered, ephemeral=True)

@reset_money.error
async def reset_money_error(interaction: discord.Interaction, error):
    embed = discord.Embed(color=color_error)

    if isinstance(error, app_commands.errors.MemberNotFound):
        embed.description = f"{emoji_error} Invalid ``<member>`` argument given.\n\nUsage:\n``/reset-money [member]``"
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed.description = f"{emoji_error} An error occurred."
        await interaction.response.send_message(embed=embed, ephemeral=True)
