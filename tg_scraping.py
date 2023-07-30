import configparser
import json
import os

from telethon.sync import TelegramClient
from telethon import connection
from dotenv import load_dotenv
# для корректного переноса времени сообщений в json
from datetime import date, datetime

# классы для работы с каналами
from telethon.tl.functions.channels import GetParticipantsRequest, ToggleParticipantsHiddenRequest
from telethon.tl.types import ChannelParticipantsSearch

# класс для работы с сообщениями
from telethon.tl.functions.messages import GetHistoryRequest

# Считываем учетные данные

load_dotenv('.env')
# Присваиваем значения внутренним переменным
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
username = os.environ['PHONE']


client = TelegramClient(username, api_id, api_hash)

client.start()


async def dump_participants(channel):
    offset_user = 0    # номер участника, с которого начинается считывание
    limit_user = 100   # максимальное число записей, передаваемых за один раз

    all_participants = []   # список всех участников канала
    filter_user = ChannelParticipantsSearch('')

    while True:
        participants = await client.get_participants(channel)
    print(participants)


async def dump_all_participants(channel):
    """Записывает json-файл с информацией о всех участниках канала/чата"""
    offset_user = 0    # номер участника, с которого начинается считывание
    limit_user = 100   # максимальное число записей, передаваемых за один раз

    all_participants = []   # список всех участников канала
    filter_user = ChannelParticipantsSearch('')

    while True:
        participants = await client(
            GetParticipantsRequest(
                channel, filter_user, offset_user, limit_user, hash=0
            )
        )
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset_user += len(participants.users)

    all_users_details = []   # список словарей с интересующими параметрами участников канала

    for participant in all_participants:
        all_users_details.append({
            "id": participant.id,
            "first_name": participant.first_name,
            "last_name": participant.last_name,
            "user": participant.username,
            "phone": participant.phone,
            "is_bot": participant.bot
        })

    with open('channel_users.json', 'w', encoding='utf8') as outfile:
        json.dump(all_users_details, outfile, indent=4, ensure_ascii=False)


async def dump_all_messages(channel):
    """Записывает json-файл с информацией о всех сообщениях канала/чата"""
    offset_msg = 0    # номер записи, с которой начинается считывание
    limit_msg = 100   # максимальное число записей, передаваемых за один раз

    all_messages = []   # список всех сообщений
    total_messages = 0
    total_count_limit = 0  # поменяйте это значение, если вам нужны не все сообщения

    class DateTimeEncoder(json.JSONEncoder):
        """Класс для сериализации записи дат в JSON"""
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            if isinstance(o, bytes):
                return list(o)
            return json.JSONEncoder.default(self, o)

    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_msg,
            offset_date=None, add_offset=0,
            limit=limit_msg, max_id=0, min_id=0,
            hash=0))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
        offset_msg = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    print(len(all_messages))
    with open('channel_messages.json', 'w', encoding='utf8') as outfile:
        json.dump(all_messages, outfile, indent=4, ensure_ascii=False, cls=DateTimeEncoder)


async def main():
    url = input("Введите ссылку на канал или чат: ")
    channel = await client.get_entity(url)
    operation = input(f"Выберите номер операции из перечня:\n"
                      f"1. Парсинг пользователей.\n"
                      f"2. Парсинг сообщений.\n"
                      f"Ввод: ")
    operation = int(operation)
    if operation == 1:
        await dump_all_participants(channel)
    elif operation == 2:
        await dump_all_messages(channel)
    elif operation == 3:
        await dump_participants(channel)
    else:
        print('Недопустимое значение.')
        return


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())