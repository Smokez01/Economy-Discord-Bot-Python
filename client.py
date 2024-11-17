import discord
from discord.ext import commands
from discord import app_commands

class CaseInsensitiveBot(commands.Bot):
    async def process_commands(self, message):
        ctx = await self.get_context(message)
        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, message):
        await self.process_commands(message)

intents = discord.Intents.all()
intents.voice_states = True

client = CaseInsensitiveBot(command_prefix='.', intents=intents, case_insensitive=True)

emoji_error = "<:error:1294366238436491295>"
emoji_success = "<:success:1294366235957530735>"
emoji_loading = "<a:loading:1294736129777602641>"
emoji_money = "<:geld:1294648227139682326>"
emoji_neutral = "<:neutral:1294658643022581892>"
emoji_transparent = "<:transparent:1294653986363805826>"
emoji_info = "<:info:1295029669044682762>"
emoji_vip = "<:vip:1294711845147377758>"
emoji_invite = "<:invite:1294709841251794966>"
emoji_login = "<:login:1295046978836627547>"
color_error = 0xb55552
color_success = 0x64b681
color_neutral = 0x1c4c82