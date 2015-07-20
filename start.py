from asyncio.tasks import sleep

_NameOfApplication_ = "BetterPollBot"

TelegramTocken = "80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY"


import  urllib.request
import urllib.parse

import json
import pprint
from time import sleep

#while(True):
print("online")
#    sleep(1)


MessageData = urllib.parse.urlencode({"limit": 1}).encode('utf-8') # data should be bytes

response = urllib.request.urlopen("https://api.telegram.org/bot"+TelegramTocken+"/getUpdates", data = MessageData).read().decode("utf-8")

#JSONresponse = json.loads(response)

#responseID = JSONresponse[]


pprint.PrettyPrinter(indent=4).pprint(json.loads(response))
'''
#url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None

MessageData = urllib.parse.urlencode({ "chat_id": 32301786, "text": "Hallo World" }).encode('utf-8') # data should be bytes

req = urllib.request.Request("https://api.telegram.org/bot" + TelegramTocken + "/sendMessage", data= MessageData )

with urllib.request.urlopen(req) as response:
   the_page = response.read()
'''

print("offline")
