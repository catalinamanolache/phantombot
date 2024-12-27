import json
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get discord token
token = os.getenv('DISCORD_TOKEN')

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