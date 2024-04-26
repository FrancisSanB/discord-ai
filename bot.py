import discord
from discord.ext import commands
import os
import torch

from langchain_ibm import WatsonxLLM
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

# Grab api_key from text file
token_file_path = 'watsonx_key.txt'
api_key = ''
with open(token_file_path, 'r') as file:
    api_key = file.read().strip()

creds = {
    'apikey': api_key,
    'url': 'https://us-south.ml.cloud.ibm.com'
}

parameters = {
    GenParams.DECODING_METHOD: DecodingMethods.SAMPLE.value,
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.TEMPERATURE: 0.5,
    GenParams.TOP_K: 50,
    GenParams.TOP_P: 1
}

llm = WatsonxLLM(
    model_id='meta-llama/llama-2-70b-chat',
    url=creds["url"],
    apikey=creds["apikey"],
    project_id='96b8df82-8c8c-4308-9a38-40bbf70b0960',
    params = parameters
)


intents = discord.Intents.default()
intents.message_content = True
CHANNEL_ID = 1215757579352014958    

# Grab token from text file
token_file_path = 'bot_token.txt'
token = ''
with open(token_file_path, 'r') as file:
    token = file.read().strip()


# Initialize your bot. Bot can be summoned with "!name"
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

@bot.command(name='noodlemaster')
async def generate_response(ctx, *, prompt: str):

    response = llm(prompt)
    # Send the response back to the channel
    await ctx.send(response)
    
# Run your bot
bot.run(token)

"""Install the required libraries (discord.py and transformers) using
pip install discord.py transformers torch

Customize the model_name variable to the specific Hugging Face model you want to use (e.g., ‘gpt2’, ‘gpt2-medium’, etc.).

When a user types !noodlemaster "prompt goes here" in a Discord channel, the bot will generate a response based on the provided prompt using the specified model.
"""

