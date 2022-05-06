import json

from utils import *
from models.news import News
from telebot import TeleBot, types
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()


def show_news(msg: types.Message, bot: TeleBot):
    lang = language_check(msg.chat.id)

    news_query = News.select().where(News.on_list == True).limit(5)

    buttons = []
    ss = content['news'][lang]['title']
    ii = 1
    for i in news_query:
        ss += str(ii) + f'. <b>{i.title}</b>\n'
        buttons.append(InlineKeyboardButton(ii, callback_data=f'news_{i.id}'))
        ii += 1

    if len(buttons) == 0:
        ss = content['news'][lang]['news_not_yet']

    reply_markup = InlineKeyboardMarkup([buttons]).to_json()    

    print(msg)
    if msg.json['from']['id'] != msg.json['chat']['id']:
        bot.edit_message_text(ss, chat_id=msg.json['chat']['id'], message_id=msg.message_id, reply_markup=reply_markup, parse_mode='html')
        return

    bot.send_message(msg.json['chat']['id'], ss, reply_markup=reply_markup, parse_mode='html')

def callback_get_news_by_id(query: types.CallbackQuery, bot: TeleBot):
    if query.data == 'news_exit':
        bot.clear_step_handler_by_chat_id(chat_id=query.message.chat.id)
        show_news(query.message, bot)
        return

    lang = language_check(query.from_user.id)

    news_id = query.data.split('_')[1]
    news_query = News.get(News.id == news_id)
    text = '<b>' + news_query.title + '</b>\n\n' + news_query.content

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='news_exit')]]).to_json()

    bot.edit_message_text(text, query.message.chat.id, query.message.id, reply_markup=reply_markup, parse_mode='html')
