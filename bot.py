import asyncio
import json
import random
import yt_dlp
import discord
import os
import requests

from discord.ext import commands
from dotenv import load_dotenv
from discord.ext import tasks

# Load environment variables
load_dotenv()

# Get discord token, channel id and weather api key from environment variables
token = os.getenv('token')
channel_id = int(os.getenv('channel_id'))
weather_api_key = os.getenv('weather_api_key')

# Create the intents object
intents = discord.Intents.default()

# Enable reading message content
intents.message_content = True

# Open the config file and load the information
with open('config.json', 'r') as f:
    config = json.load(f)

# Get prefix from config file
prefix = config['prefix']

# Create the bot instance
bot = commands.Bot(command_prefix=prefix, intents=intents)

# Event to print a message when the bot is active
@bot.event
async def on_ready():
    channel = bot.get_channel(channel_id)
    await channel.send('Hello! I am now online!')
    scheduled_event.start()

# Event to print a welcome message when a new member joins the server
@bot.event
async def on_member_join(member):
    channel = bot.get_channel(channel_id)
    await channel.send(f'Welcome to the server, {member.mention}!')

# Event that is scheduled every 2 minutes to send a message
@tasks.loop(seconds=120)  
async def scheduled_event():
    channel = bot.get_channel(channel_id)
    await channel.send('Have a good day! This is the PhantomBot demo!')

# Event to handle custom user messages
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

# Reminder command with time and message
@bot.command()
async def remind(ctx, time: int, *, message):
    await ctx.send(f'Reminder set for {time} seconds!')
    await asyncio.sleep(time)
    await ctx.send(f'Reminder: {message}')

# Command to get the weather for a specific location
@bot.command()
async def weather(ctx, *, location: str):
    # URL for OpenWeatherMap API with the location and API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"

    # Make the request to the weather API
    response = requests.get(url)

    # Check if the response is successful
    if response.status_code == 200:
        data = response.json()

        # Extract weather data from the API response
        city = data['name']
        temperature = data['main']['temp']
        description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        # Send the weather information to the channel
        await ctx.send(f"Weather in {city}:\n"
                       f"Temperature: {temperature}°C\n"
                       f"Description: {description}\n"
                       f"Humidity: {humidity}%\n"
                       f"Wind Speed: {wind_speed} m/s")
    else:
        await ctx.send("Sorry, I couldn't fetch the weather data. Please check the location and try again.")

# Moderation commands
# Command to kick a user
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked.')

# Command to ban a user
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f'{member} has been banned.')

# Command to mute a user
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

# Command to warn a user for a specific reason
@bot.command()
@commands.has_permissions(manage_roles=True)
async def warn(ctx, member: discord.Member, *, reason=None):
    await ctx.send(f'{member} has been warned for: {reason}')

# Command to unmute a user
@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    # Get the mute role
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")

    if mute_role not in member.roles:
        await ctx.send(f'{member} is not muted.')
        return

    # Remove the mute role
    await member.remove_roles(mute_role)
    await ctx.send(f'{member} Unmuted.')

# Command for the bot tp join the voice channel in which the user currently is
@bot.command()
async def join(ctx):
    # Check if the user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to join a voice channel first!")
        return

    # Connect to the voice channel
    channel = ctx.author.voice.channel
    await channel.connect()

# Command to play a song from YouTube
@bot.command()
async def play(ctx, url: str):
    # Check if the bot is connected to a voice channel
    if not ctx.voice_client:
        if not ctx.author.voice:
            await ctx.send("You need to join a voice channel first!")
            return
        channel = ctx.author.voice.channel
        await channel.connect()

    # Options for the YouTube downloader
    ytdl_opts = {
        'format': 'bestaudio/best',  # This will select the best audio format
        'extractaudio': True,  # Ensures only audio is downloaded
        'audioquality': 1,  # Highest audio quality
        'outtmpl': 'downloads/%(id)s.%(ext)s',  # Save the audio in a specific directory
        'restrictfilenames': True,  # Avoid spaces in file names
        'noplaylist': True,  # Avoid downloading playlists
        'quiet': False,  # Show verbose output for debugging
    }

    # FFmpeg options
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
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
        # Send an error message if an exception occurs
        await ctx.send(f"An error occurred: {str(e)}")

# Command to stop the music and disconnect from the voice channel
@bot.command()
async def stop(ctx):
    # Stop the music and disconnect from the voice channel
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to any voice channel.")

# Command to pause the music
@bot.command()
async def pause(ctx):
    # Pause the music
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("Music paused.")
    else:
        await ctx.send("No music is currently playing.")

# Command to resume the paused music
@bot.command()
async def resume(ctx):
    # Resume the music
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("Music resumed.")
    else:
        await ctx.send("No music is currently paused.")

# Command to skip the current song
@bot.command()
async def skip(ctx):
    # Skip the current song
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Music skipped.")
    else:
        await ctx.send("No music is currently playing.")


# Random jokes list
jokes = [
    "Why don't skeletons fight each other? They don't have the guts.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don’t oysters donate to charity? Because they are shellfish.",
    "I'm on a seafood diet. I see food and I eat it.",
    "What do you call fake spaghetti? An impasta.",
    "Why don’t seagulls fly over the bay? Because then they’d be bagels!",
    "I told my computer I needed a break, and now it won’t stop sending me Kit-Kats.",
    "Why was the math book sad? Because it had too many problems.",
    "I used to play piano by ear, but now I use my hands.",
    "What do you call a fish with no eyes? A fsh.",
    "Why can’t your nose be 12 inches long? Because then it would be a foot.",
    "I told my wife she was drawing her eyebrows too high. She seemed surprised.",
    "Why don't eggs tell jokes? Because they'd crack each other up!",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "What did one ocean say to the other ocean? Nothing, they just waved.",
    "I’m reading a book on anti-gravity. It’s impossible to put down!",
    "Why don't skeletons ever use cell phones? They don’t have the guts.",
    "I’m no good at math, but I know that 7 days without a pun makes one weak.",
    "Why don’t some couples go to the gym? Because some relationships don’t work out.",
    "What’s orange and sounds like a parrot? A carrot."
]

# Command to get a random joke from the list
@bot.command()
async def joke(ctx):
    random_joke = random.choice(jokes)
    await ctx.send(random_joke)

bot.run(token)
