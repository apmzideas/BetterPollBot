from asyncio.tasks import sleep

_NameOfApplication_ = "BetterPollBot"

TelegramToken = "80578257:AAEt5tHodsbD6P3hqumKYFJAyHTGWEgcyEY"


import  urllib.request
import urllib.parse

import json
import pprint
from time import sleep

#while(True):

print("online")

#    sleep(1)


MessageData = urllib.parse.urlencode({"limit": 1}).encode('utf-8') # data should be bytes

response = urllib.request.urlopen("https://api.telegram.org/bot"+TelegramToken+"/getUpdates", data = MessageData).read().decode("utf-8")

#JSONresponse = json.loads(response)

#responseID = JSONresponse[]


pprint.PrettyPrinter(indent=4).pprint(json.loads(response))

#url, data=None, headers={}, origin_req_host=None, unverifiable=False, method=None

MessageData = urllib.parse.urlencode({ "chat_id": 10620786, "text": b'Hallo World \xF0\x9F\x98\x81' }).encode('utf-8') # data should be bytes

req = urllib.request.Request("https://api.telegram.org/bot" + TelegramToken + "/sendMessage", data= MessageData )

with urllib.request.urlopen(req) as response:
   the_page = response.read()


print("offline")
