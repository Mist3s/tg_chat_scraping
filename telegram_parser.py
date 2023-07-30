import os
from collections import deque
from telethon import TelegramClient, events
from telethon.tl.functions.messages import (
    GetDialogsRequest, GetHistoryRequest
)
from telethon import functions, types
from dotenv import load_dotenv

load_dotenv('.env')
api_id = os.environ['API_ID']
api_hash = os.environ['API_HASH']
bot_token = os.environ['TOKEN']


def telegram_parser(session, api_id, api_hash, telegram_channels, posted_q,
                    n_test_chars=50, check_pattern_func=None,
                    send_message_func=None, logger=None, loop=None):
    """Телеграм парсер."""

    # Ссылки на телеграмм каналы, значение из словаря telegram_channels
    # помещаем в список telegram_channels_links.
    telegram_channels_links = list(telegram_channels.values())
    # Авторизуемся в клиенте.
    client = TelegramClient(session, api_id, api_hash,
                            base_logger=logger, loop=loop).start(bot_token=bot_token)

    @client.on(events.NewMessage(pattern='/(?i)start'))
    async def start(event):
        sender = await event.get_sender()
        sender = sender.id
        text = 'test test'
        await client.send_message(sender, text)

    # Используя декоратор client.on с параметром events.NewMessage
    # и значение chats = ссылки на каналы.
    @client.on(events.NewMessage(chats=telegram_channels_links))
    async def handler(event):
        '''Забирает посты из телеграмм каналов и посылает их в наш канал'''
        print('start_scraping')
        if event.raw_text == '':
            return

        # print(event.stringify())
        news_text = ' '.join(event.raw_text.split('\n')[:2])

        if not (check_pattern_func is None):
            if not check_pattern_func(news_text):
                return

        head = news_text[:n_test_chars].strip()

        if head in posted_q:
            return

        source = telegram_channels[event.message.peer_id.channel_id]

        link = f'{source}/{event.message.id}'

        channel = '@' + source.split('/')[-1]

        post = f'<b>{channel}</b>\n{link}\n{news_text}'

        if send_message_func is None:
            print(post, '\n')
        else:
            await send_message_func(post)

        posted_q.appendleft(head)
        print(event.message.media.photo.id)

        # def callback(current, total):
        #     print('Downloaded', current, 'out of', total,
        #           'bytes: {:.2%}'.format(current / total))
        # await client.download_media(event.message.media, progress_callback=callback)
        await event.forward_to(1505379330)
        # await client.send_message(1505379330, event.message)

    return client


if __name__ == "__main__":

    telegram_channels = {
        # 1521612455: 'https://t.me/zavarka39_ru',
        1505379330: 'https://t.me/scrapingtestq',
        # 1101170442: 'https://t.me/rian_ru',
        # 1133408457: 'https://t.me/prime1',
        # 1149896996: 'https://t.me/interfaxonline',
        # 1001029560: 'https://t.me/bcs_express',
        # 1203560567: 'https://t.me/markettwits',
    }

    # Очередь из уже опубликованных постов, чтобы их не дублировать
    posted_q = deque(maxlen=20)

    client = telegram_parser('bot', api_id, api_hash, telegram_channels, posted_q)

    client.run_until_disconnected()
