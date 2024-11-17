import discord

def create_embed_with_title(description, image_url=None, author_name=None, author_avatar=None, color=None):
    embed = discord.Embed(description=description, color=color or 0x2d5593)
    if image_url:
        embed.set_image(url=image_url)
    if author_name:
        embed.set_author(name=author_name, icon_url=author_avatar)
    return embed