import configparser
import requests
from telethon import TelegramClient, events, sync
from telethon.errors import SessionPasswordNeededError
from alfredo import pred_class, get_response
from alfredo import words, classes, data


# Reading Configs
config = configparser.ConfigParser()
config.read("config.ini")

# Setting id and hash values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']
channel = config['Telegram']['channel']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
client.start()
print("Client Created\n")

# Ensure you're authorized
if not client.is_user_authorized():
    client.send_code_request(phone)
    try:
        client.sign_in(phone, input('Enter the code: '))
    except SessionPasswordNeededError:
        client.sign_in(password=input('Password: '))

# Get a response function
def get_response_to(msg):
    usr_inp = str(msg)
    intents = pred_class(usr_inp, words, classes)
    response = get_response(intents, data)
    return response

# Get messages and make response
@client.on(events.NewMessage(chats=channel))
async def newMessageListener(event):
    newMessage = event.message.message
    print("Message: " + str(newMessage))
    resp = get_response_to(newMessage)
    print("Response: " + resp + "\n")
    await client.send_message(channel, resp)

with client:
    client.run_until_disconnected()
