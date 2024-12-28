import asyncio
import json
import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks
from datetime import datetime

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


# Scheduled Events
@tasks.loop(seconds=120)  
async def scheduled_event():
    channel = bot.get_channel(channel_id)
    await channel.send('Have a good day! This is the PhantomBot demo!')

# Reminder command with time and message
@bot.command()
async def remind(ctx, time: int, *, message):
    await ctx.send(f'Reminder set for {time} seconds!')
    await asyncio.sleep(time)
    await ctx.send(f'Reminder: {message}')

#Custom Responses
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "hello bot" in message.content.lower():
        await message.channel.send("Hello there!")
    elif "hi bot" in message.content.lower():
        await message.channel.send("Hi! How can I assist you today?")
    elif "good morning" in message.content.lower():
        await message.channel.send("Good morning! Hope you have a great day ahead!")
    elif "good evening" in message.content.lower():
        await message.channel.send("Good evening! How's your day been?")
    elif "what is your name" in message.content.lower():
        await message.channel.send("I'm PhantomBot, nice to meet you! 😄")
    elif "how are you" in message.content.lower():
        await message.channel.send("I'm just a bot, but I'm doing great! How about you?")
    elif "what can you do" in message.content.lower():
        await message.channel.send("I can help with a variety of tasks, just ask away! 😉")
    elif "help" in message.content.lower():
        await message.channel.send("Here are some commands you can try:\n- 'hello bot' for a greeting\n- 'help' for assistance\n- 'goodbye' to say bye\n- Prefix is '!'")
    elif "goodbye" in message.content.lower():
        await message.channel.send("Goodbye! Take care! 👋")
    elif "bye" in message.content.lower():
        await message.channel.send("Bye! See you soon! 😊")


    
    await bot.process_commands(message)



bot.run(token)




