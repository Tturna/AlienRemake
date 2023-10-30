# This example requires the 'message_content' intent.

import discord
import json

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

with open('secret.json', 'r') as f:
    # cont = f.read()
    cont = json.load(f)
    client.run(cont['token'])
