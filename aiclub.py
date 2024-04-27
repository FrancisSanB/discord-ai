import discord
import os
import torch
import re  
from discord.ext import commands
from transformers import AutoModelForCausalLM, AutoTokenizer

intents = discord.Intents.default()
intents.message_content = True
CHANNEL_ID = 1220138553560924233

# Initialize your bot. Bot can be summoned with "!name"
bot = commands.Bot(command_prefix='!', intents=intents)

# Load your pre-trained model and tokenizer
model_name = 'microsoft/DialoGPT-large'
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token_id = tokenizer.eos_token_id

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command(name='bot')
async def generate_response(ctx, *, prompt: str):
    print("Received prompt:", prompt.lower())  # Print lowercase prompt for debugging

    # Define channel IDs dictionary
    channel_ids = {
        'welcome-and-rules': 1220138553099554879,
        'notes-resources': 1220138553560924230,
        'general': 1220138553560924233,
        'homework-help': 1220138553560924234,
        'session-planning': 1220138553560924235,
        'off-topic': 1220138553560924236
    }

    # Check if the prompt starts with "search for"
    if prompt.lower().startswith("search for"):
        # Extract the desired text from the prompt
        desired_text = prompt[len("search for"):].strip().lower()

        # Initialize a list to store channels where the text is found
        found_channels = []

        # Iterate over each channel in the server
        for channel_name, channel_id in channel_ids.items():
            channel = ctx.guild.get_channel(channel_id)
            # Check if the channel is a text channel
            if isinstance(channel, discord.TextChannel):
                # Iterate over messages in the channel
                async for message in channel.history(limit=None):
                    # Check if the desired text is present in the message content
                    if desired_text in message.content.lower():
                        # If the text is found, add the channel to the list and break out of the loop
                        found_channels.append(channel)
                        break
        
        # If channels with the desired text are found, list them
        if found_channels:
            response = "The text was found in the following channels:"
            for channel in found_channels:
                response += f"\n- {channel.name} ({channel.mention})"
        else:
            response = "Sorry, I couldn't find the desired text in any channel."
    else:
        # Extract mentioned channel from the prompt
        mentioned_channel = None
        for channel_name, channel_id in channel_ids.items():
            first_keyword = channel_name.split('-')[0]  # Get the first keyword of the channel name
            search_pattern = r'\b' + re.escape(first_keyword) + r'\b'  # Search for the first keyword only
            print("Search pattern:", search_pattern)
            if re.search(search_pattern, prompt.lower()):
                mentioned_channel = (channel_name, channel_id)
                break

        # Debugging: Print the mentioned channel
        print("Mentioned channel:", mentioned_channel)

        # If a channel is mentioned
        if mentioned_channel:
            channel_name, channel_id = mentioned_channel
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                response = f"You can find more information in the {channel.mention} channel."
            else:
                response = f"Sorry, I can't access the '{channel_name}' channel. It might be hidden or I don't have permission to view it."
        else:
            # Tokenize the input prompt
            input_ids = tokenizer.encode(prompt, return_tensors='pt', max_length=64, truncation=True)

            # Generate a response from the model
            with torch.no_grad():
                output = model.generate(input_ids, do_sample=True, max_length=128, num_return_sequences=1, top_k=40, temperature=0.8, pad_token_id=tokenizer.eos_token_id)
            
            # Decode the generated response
            response = tokenizer.decode(output[0], skip_special_tokens=True)

            print("Generated response:", response)

    # Send the response back to the channel
    await ctx.send(response)

# Run your bot
bot.run(token='*')
