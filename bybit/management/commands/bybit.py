from bybit.models import Chat, ErrorLog
from bybit.func_buy_coin import buy_coin_with_stop_loss, close_part_position

from django.core.management.base import BaseCommand
from telethon.sync import TelegramClient
from telethon import events
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()


def main():
    print('Start')
    client = TelegramClient(
        "session",
        2547559,
        "1a1975ef3b460f054d2777ddf45e8faf"
    )
    client.start()
    client.get_dialogs()

    @client.on(events.NewMessage())
    async def handler_first(event):
        try:
            chats_list = []
            for chat in Chat.objects.all():
                chats_list.append(str(chat.chat_id).replace('-', '')[3:])

            print('New_message')
            try:
                have_channel_id = getattr(event.message.peer_id, 'channel_id', False)
                if have_channel_id and str(event.message.peer_id.channel_id) in chats_list:
                    print('1')
                    message = str(event.message.message)

                    if "Leverage" in message:
                        symbol = message.split("USDT")[0]
                        symbol = symbol[1:] + "USDT"

                        # side = message.split("Signal: ")[1].split("\n")[0]

                        buy_coin_with_stop_loss(symbol, "Buy")

                    elif "target" in message and "Period" in message:
                        symbol = message.split("\n")[1].split("/USDT")[0]
                        symbol = symbol[1:] + "USDT"

                        target_num = int(message.split("target")[1][1])

                        close_part_position(symbol, target_num)

            except AttributeError:
                pass
        except Exception as e:
            ErrorLog.objects.create(error=str(e))
    client.run_until_disconnected()


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def handle(self, *args, **options):
        try:
            main()
        except Exception as e:
            ErrorLog.objects.create(error=str(e))
