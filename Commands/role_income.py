import math
from client import *
from database import income_collection

roles_per_page = 5

class PaginationView(discord.ui.View):
    def __init__(self, pages, num_pages, start_page=0):
        super().__init__(timeout=180)
        self.page = start_page
        self.pages = pages
        self.num_pages = num_pages
        self.update_buttons()

    def update_buttons(self):
        self.children[0].disabled = self.page == 0
        self.children[1].disabled = self.page == self.num_pages - 1

    @discord.ui.button(label="Previous Page", style=discord.ButtonStyle.primary, custom_id="prev")
    async def prev_button(self, interaction: discord.Interaction):
        if self.page > 0:
            self.page -= 1
        self.update_buttons()
        embed = self.pages[self.page]
        embed.set_footer(text=f"Page {self.page + 1}/{self.num_pages}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next Page", style=discord.ButtonStyle.primary, custom_id="next")
    async def next_button(self, interaction: discord.Interaction):
        if self.page < self.num_pages - 1:
            self.page += 1
        self.update_buttons()
        embed = self.pages[self.page]
        embed.set_footer(text=f"Page {self.page + 1}/{self.num_pages}")
        await interaction.response.edit_message(embed=embed, view=self)

@client.tree.command(name="role-income", description="Displays roles with assigned income.")
@app_commands.describe(page_number="The page number to display")
async def role_income(interaction: discord.Interaction, page_number: int = 1):
    guild_id = str(interaction.guild.id)
    await paginate_roles(interaction, guild_id, page_number)

async def paginate_roles(interaction, guild_id, page_number):
    roles = list(income_collection.find({"guild_id": guild_id}).sort("amount", -1))
    total_roles = len(roles)
    total_pages = math.ceil(total_roles / roles_per_page)
    current_page = max(0, min(total_pages - 1, page_number - 1))

    pages = []
    for i in range(0, total_roles, roles_per_page):
        embed = discord.Embed(title="Roles with Income", color=color_neutral)
        for index, role in enumerate(roles[i:i + roles_per_page], start=i + 1):
            role_id = int(role["role_id"])
            guild = interaction.guild
            discord_role = guild.get_role(role_id)

            role_name = discord_role.name if discord_role else "Name not available"
            income_amount = role.get("amount", 0)
            embed.add_field(name=f"``{index}`` - {role_name}",
                            value=f"{emoji_money} {income_amount:,} every 24h.", inline=False)
        pages.append(embed)

    if total_pages > 0:
        view = PaginationView(pages, total_pages, start_page=current_page)
        embed = pages[current_page]
        embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")
        await interaction.response.send_message(embed=embed, view=view)
    else:
        embed = discord.Embed(description=f"{emoji_error} No roles with income found.", color=color_error)
        await interaction.response.send_message(embed=embed)
