import os
import json
from datetime import datetime
from dotenv import load_dotenv

from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest


load_dotenv('.env')
tg_api_id = os.environ['API_ID']
tg_api_hash = os.environ['API_HASH']
phone = os.environ['PHONE']


async def dump_all_messages(channel, last_message_id):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0    # номер записи, с которой начинается считывание
    limit_msg = 100   # максимальное число записей, передаваемых за один раз
    all_messages = []   # список всех сообщений
    total_messages = 0
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения
    while True:
        history = await client(
            GetHistoryRequest(
                peer=channel,
                offset_id=offset_msg,
                offset_date=None,
                add_offset=0,
                limit=limit_msg,
                max_id=0,
                min_id=last_message_id,
                hash=0
            )
        )
        messages = history.messages
        if not messages or len(messages) == 0:
            break
        for message in messages:
            all_messages.append(message.to_dict())
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    return all_messages


def write_json_file(messages):
    class DateTimeEncoder(json.JSONEncoder):
        """Класс для сериализации записи дат в JSON"""
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(messages, outfile, indent=4, ensure_ascii=False, cls=DateTimeEncoder)


def read_json_file():
    with open('channel_messages.json') as file:
        data = json.load(file)
    return data


async def main():
    try:
        last_message_id = read_json_file()[0]['id']
    except FileNotFoundError:
        last_message_id = 0
    url = 'https://t.me/scrapingtestq'
    channel = await client.get_entity(url)
    messages = await dump_all_messages(channel, last_message_id)
    if messages:
        write_json_file(messages)
    else:
        print('No new messages.')


if __name__ == '__main__':
    client = TelegramClient(phone, tg_api_id, tg_api_hash)
    client.start()
    with client:
        client.loop.run_until_complete(main())
