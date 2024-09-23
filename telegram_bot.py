import telegram


class TelegramHandler:
    def __init__(self, token: str, id: str) -> None:
        self.activated = False
        self.token = token if (token != None) else input("Provide Telegram token:")
        self.bot_channel_id = id if (id != None) else input("Provide Telegram channel id:")
        try:
            self.bot = telegram.Bot(token=self.token)
            self.activated = True
        except Exception as e:
            print(e)

    def send_message(self, chat_id: int, text: str) -> None:
        if (self.activated):
            self.bot.send_message(chat_id=chat_id, text=text)
        else:
            print("Message not send to the telegram bot. Token/channel wrong or not provided.")
