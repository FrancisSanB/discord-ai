import discord
from discord.ext import commands,tasks
import os
from dotenv import load_dotenv
import yt_dlp as youtube_dl

from functions import *

load_dotenv()

# Get the API token from the .env file.
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!',intents=intents)

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else ytdl.prepare_filename(data)
        return filename
    
@bot.event
async def on_ready():
    print("The bot is ready!")

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

@bot.command(name='leave', help='To make the bot leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")

@bot.command(name='play_song', help='To play song')
async def play(ctx,url):
    try:
        # Get the user's voice channel
        voice_channel = ctx.author.voice.channel
        
        if voice_channel:
            # Check if the bot is already in a voice channel
            if ctx.voice_client is None:
                # Connect to the user's voice channel
                voice_client = await voice_channel.connect()
            else:
                # Move to the user's voice channel if already connected
                await ctx.voice_client.move_to(voice_channel)
            
            # Download and play the audio
            async with ctx.typing():
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                ctx.voice_client.play(discord.FFmpegPCMAudio(executable=r"C:\Users\f_alf\Documents\ai-club\discord-ai\ffmpeg.exe", source=filename))
            
            await ctx.send('**Now playing:** {}'.format(filename))
        else:
            await ctx.send("You need to be in a voice channel to use this command.")
    except Exception as e:
        print(e)
        await ctx.send("An error occurred while trying to play the song.")

@bot.command(name='pause', help='This command pauses the song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    
@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        await voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@bot.command(name='stop', help='Stops the song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        await voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='quote', help='inspires with a quote')
async def on_message(ctx):
    quote = get_quote()
    await ctx.channel.send(quote)

@bot.command(name='translate', help='translates text')
async def translate(ctx, target_language: str, *, prompt: str):
    text = translate_text(prompt, target_language)
    if text == 'ERROR':
        await ctx.send("Invalid target language. Please provide a valid language code (e.g., 'de' for German).")
    else:
        await ctx.send(f"Translated text ({target_language}): {text}")

@bot.command(name='audio-to-text', help='goes from audio to text')
async def audiototext(ctx):
    # Check if the user attached an audio file
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach an audio file.")
        return

    # Get the first attached file
    audio_file = ctx.message.attachments[0]

    # Save the audio file locally
    audio_path = "temp_audio.wav"
    await audio_file.save(audio_path)

    # Simulate typing
    async with ctx.typing():
        # Convert audio to text
        text = audiotext(audio_path)

    # Send the text back to the user
    await ctx.send(text)

@bot.command(name='audio-translate-text', help='goes from audio to text that you want to translate')
async def audiotranstext(ctx, target_language: str):
# Check if the user attached an audio file
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please attach an audio file.")
        return

    # Get the first attached file
    audio_file = ctx.message.attachments[0]

    # Save the audio file locally
    audio_path = "temp_audio.wav"
    await audio_file.save(audio_path)

    # Simulate typing
    async with ctx.typing():
        # Convert audio to text
        script = audiotext(audio_path)
        text = translate_text(script, target_language)

    # Send the text back to the user
    await ctx.send(f"Translated text ({target_language}): {text}")

@bot.command(name='play-text', help='Plays text in a voice channel')
async def playtext(ctx, *, prompt: str):
    try:
        # Get the user's voice channel
        voice_channel = ctx.author.voice.channel

        if voice_channel:
            # Connect to the user's voice channel or move if already connected
            voice_client = ctx.voice_client or await voice_channel.connect()

            # Download and play the audio
            async with ctx.typing():
                texttomp3(prompt)
                voice_client.play(discord.FFmpegPCMAudio("output.mp3"))

            await ctx.send(f"**Now playing:** {prompt}")
        else:
            await ctx.send("You need to be in a voice channel to use this command.")
    except AttributeError:
        await ctx.send("You need to be in a voice channel to use this command.")
    except Exception as e:
        print(e)
        await ctx.send("An error occurred while trying to play the audio.")

@bot.command(name='image-text', help='extracts the text from an image')
async def extract_text(ctx):
    try:
        # Check if there are any attachments
        if not ctx.message.attachments:
            await ctx.send("Please attach an image to extract text.")
            return

        # Get the first attachment (assuming only one image is attached)
        attachment = ctx.message.attachments[0]

        # Save the attachment to a temporary file
        image_path = "temp_image.jpg"
        await ctx.send("Downloading the image...")
        await attachment.save(image_path)

        async with ctx.typing():
            result = imagetotext(image_path)

        # Send the result back to the user
        await ctx.send(f"Extracted text:\n```\n{result}\n```")
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)