import locale, random, os, importlib
from dotenv import load_dotenv
from discord.ext import tasks
from client import *
from database import *

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

try:
    locale.setlocale(locale.LC_ALL, '')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'C.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'C')

base_dir = os.path.dirname(os.path.abspath(__file__))

commands_path = os.path.join(base_dir, "Commands")
events_path = os.path.join(base_dir, "Events")

for filename in os.listdir(commands_path):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = os.path.splitext(filename)[0]
        importlib.import_module(f"Commands.{module_name}")

for filename in os.listdir(events_path):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = os.path.splitext(filename)[0]
        importlib.import_module(f"Events.{module_name}")

status_messages = [
    "made by Smokez01.",
    "for anyone",
]

@client.event
async def on_command_error(ctx, error):
    if hasattr(error, 'handled') and error.handled:
        return

    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Cooldown",
                              description=f"Please wait {error.retry_after:.2f} seconds before using this command again.",
                              color=0xdd5d56)
        await ctx.send(embed=embed)
        error.handled = True
    else:
        embed = discord.Embed(title="Error",
                              description=f"An error occurred: {type(error).__name__} - {error}",
                              color=0xFF0000)
        await ctx.send(embed=embed)
        error.handled = True

@tasks.loop(minutes=10)
async def change_status():
    activity = discord.Streaming(name=random.choice(status_messages), url="https://www.twitch.tv/smokez_games")
    await client.change_presence(activity=activity)

@client.event
async def on_ready():
    print(f"🤖 {client.user.name} is logged in!")
    try:
        change_status.start()
        await client.tree.sync()
        print("Slash commands synced successfully!")
    except Exception as e:
        print(f"Error during on_ready: {e}")

async def shutdown():
    await client.wait_until_ready()
    await client.close()

@client.event
async def on_error(*args):
    if args and isinstance(args[0], discord.errors.InteractionResponded):
        return

    raise

async def adjust_money_in_account(user_id, amount, guild_id):
    user_data = money_collection.find_one({"guild_id": guild_id, "user_id": str(user_id)})

    if user_data:
        current_bank = user_data.get("bank", 0)
        new_bank = current_bank + amount

        money_collection.update_one(
            {"guild_id": guild_id, "user_id": str(user_id)},
            {"$set": {"bank": new_bank}}
        )
    else:
        if amount >= 0:
            money_collection.insert_one(
                {"guild_id": guild_id, "user_id": str(user_id), "cash": 0, "bank": amount}
            )
        else:
            money_collection.insert_one(
                {"guild_id": guild_id, "user_id": str(user_id), "cash": 0, "bank": 0}
            )

try:
    client.run(TOKEN)
except KeyboardInterrupt:
    print('The program was terminated.')