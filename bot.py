import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re 
import requests


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Url for Random.org's API
URL = os.getenv('RANDOM_API_URL')
API_TOKEN = os.getenv('RANDOM_API_TOKEN')



class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        print("saw message")

        command = re.search("^\!roll ([0-9]+)d([0-9]+)",message.content)
        if command:
            print("-----")
            print("worked")
            dice_amount = min(25, int(command.group(1)))
            dice_size = min(30, int(command.group(2)))
            reply = "Invalid request."
            #This block of the code handles the interaction with the Random.org API
            if dice_amount>0 and dice_size>0:
                post_request = {
	                "jsonrpc": "2.0",
                    "method": "generateIntegers",
	                "params": {
		                "apiKey": "692804ed-4760-45f3-928f-c83daa7f11b1",
		                "n": dice_amount,
		                "min": 1,
		                "max": dice_size},
	                "id": "pancake"
                    }	
                response = requests.post(URL, json = post_request)
                if response.ok:
                    post_response = response.json()
                
                    print(post_response)
                    data = sorted(post_response['result']['random']['data'])
                    reply = "Roll Results: [" + ", ".join([str(x) for x in data]) + "]"
                    await message.reply(reply, mention_author=True)
                else:
                    await message.reply("Request could not be processed.", mention_author=True)
        else:
            print("didn't work")

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)