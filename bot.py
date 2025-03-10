import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import re 
import requests
import datetime
import json 

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

#Url for Random.org's API
URL = os.getenv('RANDOM_API_URL')
API_TOKEN = os.getenv('RANDOM_API_TOKEN')

def get_last_date() -> datetime.datetime:
    since_date = datetime.datetime.now(datetime.timezone.utc)
    try:
        last_date = open("last_date.json", "r")
        data = json.loads(last_date.readline())
        since_date = datetime.datetime.fromisoformat(data.get("date"))
        last_date.close()
    except: 
        print("No previous datetime")
    return since_date

def set_last_date():
    last_date = open("last_date.json", "w")
    last_date.write(json.dumps({"date": datetime.datetime.isoformat(datetime.datetime.now(datetime.timezone.utc))}))
    last_date.close()





class MyClient(discord.Client):

    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        since_date = get_last_date()
        print(f'Last run on {datetime.datetime.isoformat(since_date)}')
        await self.check_old_messages()


    async def check_old_messages(self):
        since_date = get_last_date()
        for guild in self.guilds:
            for channels in guild.text_channels:
                messages = [message async for message in channels.history(after= since_date )]
                for message in messages:
                    await self.on_message(message)
        set_last_date()
        
    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return
        print("saw message")

        command = re.search("^\!roll ([0-9]+)d([0-9]+)([+-][0-9]+)?",message.content)
        if command:
            print("-----")
            print("worked")
            dice_amount = min(25, int(command.group(1)))
            dice_size = min(100, int(command.group(2)))
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
		    set_last_date()
                    post_response = response.json()
                
                    print(post_response)
                    data = sorted(post_response['result']['random']['data'])
                    values = "Roll Results: [" + ", ".join([str(x) for x in data]) + "]"
                    if command.group(3):
                        reply = "Sum: " + str(sum(data) + (int(command.groups()[2][1:]) if command.groups()[2][0] == "+" else -1 * int(command.groups()[2][1:]))) 
                        reply = reply + "\n" + values
                    else:
                        reply = values               
                    await message.reply(reply, mention_author=True)
                else:
                    await message.reply("Request could not be processed.", mention_author=True)
        else:
            print("didn't work")

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(TOKEN)
