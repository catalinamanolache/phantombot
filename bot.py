
import json
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get discord token and channel id
token = os.getenv('token')
channel_id = int(os.getenv('channel_id'))

# Create bot instance
intents = discord.Intents.default()

# Enable reading message content
intents.message_content = True

client = discord.Client(intents=intents)

with open('config.json', 'r') as f:
    config = json.load(f)

# Get prefix from config file
prefix = config['prefix']

bot = commands.Bot(command_prefix=prefix, intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(channel_id)
    await channel.send('Hello! I am now online!')
    scheduled_event.start()


#Scheduled Events
from discord.ext import tasks
from datetime import datetime

@tasks.loop(seconds=120)  
async def scheduled_event():
    channel = bot.get_channel(channel_id)
    await channel.send('Have a good day! This is the PhantomBot demo!')


bot.run(token)


