import pytz
from datetime import datetime
from client import *
from database import money_collection, income_collection
from Events.create_embed_with_title import create_embed_with_title
from Events.calculate_next_collect_time import calculate_next_collect_time

@client.tree.command(name="collect", description="Collects your income based on roles.")
async def collect(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    guild_id = str(interaction.guild.id)

    existing_user = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})
    if not existing_user:
        datetime.now(pytz.utc).isoformat()
        money_collection.insert_one({
            "guild_id": guild_id,
            "user_id": user_id,
            "bank": 0,
            "last_collect": {},
            "collected_roles": []
        })
        existing_user = money_collection.find_one({"guild_id": guild_id, "user_id": user_id})

    last_collect_times = existing_user.get("last_collect", {})
    collected_roles = existing_user.get("collected_roles", [])

    total_income = 0
    income_sources = []
    user_roles = interaction.user.roles
    cooldown_messages = []
    new_roles = []

    for role in user_roles:
        role_data = income_collection.find_one({"guild_id": guild_id, "role_id": str(role.id)})
        if role_data:
            role_id = str(role.id)
            role_income = role_data.get("amount", 0)
            cooldown_hours = role_data.get("cooldown", 24)
            last_collect_time = last_collect_times.get(role_id)
            next_collect_time = calculate_next_collect_time(last_collect_time, cooldown_hours)

            if datetime.now(pytz.utc) >= next_collect_time:
                total_income += role_income
                new_roles.append(role_id)
                income_sources.append(f"{role.name} | {emoji_money} {role_income:,.0f}")
                last_collect_times[role_id] = datetime.now(pytz.utc).isoformat()
            else:
                timestamp = int(next_collect_time.timestamp())
                cooldown_messages.append(f"{role.name} | Collectible at <t:{timestamp}:R>")

    collected_roles.extend([role for role in new_roles if role not in collected_roles])

    if total_income > 0:
        money_collection.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {
                "$set": {
                    "bank": existing_user['bank'] + total_income,
                    "last_collect": last_collect_times,
                    "collected_roles": collected_roles
                }
            }
        )

        embed = create_embed_with_title(
            description=f"{emoji_success} You've received your income of {total_income:,.0f} <:money:emoji_money>!\n\nIncome sources:\n" + "\n".join(income_sources),
            author_name=interaction.user.name,
            author_avatar=interaction.user.avatar.url,
            color=color_success
        )
        await interaction.response.send_message(embed=embed)
    else:
        cooldown_info = "\n".join(cooldown_messages) if cooldown_messages else "No cooldowns available."
        embed = create_embed_with_title(
            description=f"{emoji_error} You can't collect income right now. Please wait until your roles become collectible again.\n\nCooldowns:\n{cooldown_info}",
            author_name=interaction.user.name,
            author_avatar=interaction.user.avatar.url,
            color=color_error
        )
        await interaction.response.send_message(embed=embed, ephemeral=False)
