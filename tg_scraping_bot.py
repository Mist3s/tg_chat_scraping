import os
from collections import deque
from dotenv import load_dotenv

from telethon import TelegramClient, events
from telethon.tl.types import InputMediaPhoto, InputPeerEmpty
from telethon.tl.functions.messages import UploadMediaRequest, GetDialogsRequest

load_dotenv('.env')
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
bot_token = os.environ['TOKEN']

telegram_channels = {
        # 1973987446: 'https://t.me/post_test_t',
        1505379330: 'https://t.me/scrapingtestq',
    }

posted_q = deque(maxlen=20)
session = 'bot'
# Ссылки на телеграмм каналы, значение из словаря telegram_channels
# помещаем в список telegram_channels_links.
telegram_channels_links = list(telegram_channels.values())
# Авторизуемся в клиенте.
client = TelegramClient(session, api_id, api_hash) #.start(bot_token=bot_token)
client.start()


@client.on(events.NewMessage(pattern='/(?i)start'))
async def start(event):
    sender = await event.get_sender()
    sender = sender.id
    text = 'test test'
    await client.send_message(sender, text)


@client.on(events.Album(chats=telegram_channels_links))
async def handler(event):
    # print(event.stringify())
    # grouped_id = event.message.grouped_id
    # media_file = event.message.media
    # print(event.message.grouped_id)
    # msg = event.messages[0].id
    # print('Got an album with', len(event), 'items')
    # print(msg)
    # Forwarding the album as a whole to some chat


    # await client.send_message(
    #     1973987446,
    #     file=event.messages,  # event.messages is a List - meaning we're sending an album
    #     message=event.original_update.message.message,  # get the caption message from the album
    # )
    await client.send_file(  # Note this is send_file not send_message
        1973987446,
        file=event.messages,
        caption=list(map(lambda a: str(a.message), event.messages))
    )


client.run_until_disconnected()
