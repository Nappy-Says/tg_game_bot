import json
from utils import *
from telebot import TeleBot, types

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()


def show_menu(msg: types.Message, bot: TeleBot):
    lang = language_check(msg.from_user.id)
    bot.send_message(msg.chat.id, content['menu'][lang]['message'])
