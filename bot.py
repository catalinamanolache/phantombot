import asyncio
import json
import random

import yt_dlp
import yt_dlp as youtube_dl
import discord
import os

import requests
from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks
from datetime import datetime

# Load environment variables
load_dotenv()

# Get discord token and channel id
token = os.getenv('token')
channel_id = int(os.getenv('channel_id'))
weather_api_key = os.getenv('weather_api_key')

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


# # TODO: Command to check the weather
# @bot.command()
# async def weather(ctx, *, location: str):
#     """Get the weather for a specific location"""
#     # URL for OpenWeatherMap API with your API key
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"
#
#     print(url)
#     # Make the request to the weather API
#     response = requests.get(url)
#
#     if response.status_code == 200:
#         data = response.json()
#
#         # Extract weather data from the API response
#         city = data['name']
#         temperature = data['main']['temp']
#         description = data['weather'][0]['description']
#         humidity = data['main']['humidity']
#         wind_speed = data['wind']['speed']
#
#         # Send the weather information to the channel
#         await ctx.send(f"Weather in {city}:\n"
#                        f"Temperature: {temperature}°C\n"
#                        f"Description: {description}\n"
#                        f"Humidity: {humidity}%\n"
#                        f"Wind Speed: {wind_speed} m/s")
#     else:
#         await ctx.send("Sorry, I couldn't fetch the weather data. Please check the location and try again.")


# Command to start the quiz
@bot.command()
async def quiz(ctx):
    """Start a quiz by letting the user choose a category"""
    # Define categories and questions
    categories = {
        "Python Basics": {
            "What is the output of the following code? `print(3 * 7)`": "21",
            "What is the keyword to define a function in Python?": "def",
            "What does `len()` do in Python?": "Returns the length of an object (string, list, etc.)"
        },
        "Python Intermediate": {
            "What is a lambda function in Python?": "A small anonymous function",
            "What is the output of the following code? `print('hello'.capitalize())`": "Hello",
            "What does `range()` do in Python?": "Generates a sequence of numbers"
        },
        "Python Advanced": {
            "What is the difference between shallow copy and deep copy in Python?": "A shallow copy copies the outer object, but deep copy copies everything recursively",
            "What is a decorator in Python?": "A function that modifies the behavior of another function",
            "What does the `with` statement do in Python?": "It manages resources like file handling"
        }
    }

    # List categories
    category_list = ", ".join(categories.keys())
    await ctx.send(f"Please choose a category from the following options: {category_list}\nYou can type the name of the category.")

    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

    try:
        # Wait for user to select a category
        msg = await bot.wait_for("message", timeout=30.0, check=check)

        # Get the selected category
        selected_category = msg.content.strip()

        # Check if the category is valid
        if selected_category not in categories:
            await ctx.send(f"Invalid category! Available categories are: {category_list}")
            return

        # Proceed with the quiz
        await ctx.send(f"Starting quiz for category: {selected_category}")
        questions = categories[selected_category]
        question, answer = random.choice(list(questions.items()))
        await ctx.send(question)

        def answer_check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel

        # Wait for the user's response
        response = await bot.wait_for("message", timeout=15.0, check=answer_check)
        if response.content.lower() == answer.lower():
            await ctx.send("Correct!")
        else:
            await ctx.send(f"Wrong! The correct answer was: {answer}.")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to respond!")

# Welcome Messages
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(channel_id)
    await channel.send(f'Welcome to the server, {member.mention}!')

#Moderation Commands
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked.')

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} has been banned.')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason=None):
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(mute_role, speak=False, send_messages=False)
    await member.add_roles(mute_role)
    await ctx.send(f'{member} has been muted.')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f'{member} has been warned for: {reason}')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    """Dezactivează mutarea unui membru (îi permite să vorbească din nou)"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if mute_role not in member.roles:
        await ctx.send(f'{member} is not muted.')
        return

    await member.remove_roles(mute_role)
    await ctx.send(f'{member} Unmuted.')


FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

@bot.command()
async def join(ctx):
    """Command to join the voice channel"""
    if not ctx.author.voice:
        await ctx.send("You need to join a voice channel first!")
        return
    channel = ctx.author.voice.channel
    await channel.connect()

@bot.command()
async def play(ctx, url: str):
    """Play a song from YouTube"""
    # Check if the bot is connected to a voice channel
    if not ctx.voice_client:
        if not ctx.author.voice:
            await ctx.send("You need to join a voice channel first!")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    ytdl_opts = {
        'format': 'bestaudio/best',  # This will select the best audio format
        'extractaudio': True,  # Ensures only audio is downloaded
        'audioquality': 1,  # Highest audio quality
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save the audio in a specific directory
        'restrictfilenames': True,  # Avoid spaces in file names
        'noplaylist': True,  # Avoid downloading playlists
        'quiet': False,  # Show verbose output for debugging
    }

    # Create a downloader object
    ytdl = yt_dlp.YoutubeDL(ytdl_opts)

    try:
        # Use yt-dlp to extract audio URL
        info_dict = ytdl.extract_info(url, download=False)
        audio_url = info_dict['url']

        # Play the audio using FFmpeg
        ctx.voice_client.play(discord.FFmpegPCMAudio(audio_url, **FFMPEG_OPTIONS))

        # Send a message about the song playing
        await ctx.send(f"Now playing: {info_dict['title']}")
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")

@bot.command()
async def stop(ctx):
    """Stop the music and disconnect from the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to any voice channel.")

@bot.command()
async def pause(ctx):
    """Pause the music"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused.")
    else:
        await ctx.send("No music is currently playing.")

@bot.command()
async def resume(ctx):
    """Resume the paused music"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed.")
    else:
        await ctx.send("No music is currently paused.")

@bot.command()
async def skip(ctx):
    """Skip the current song"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Music skipped.")
    else:
        await ctx.send("No music is currently playing.")

bot.run(token)




