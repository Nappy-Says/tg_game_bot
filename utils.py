import sys
import json
sys.path.append('../')
from telebot import TeleBot, types

from telebot import TeleBot
from models.users import Users
from models.games import GamesSession as GS

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()

def send_error(chat_id: int, bot: TeleBot, msg: str = ''):
    if msg == '':
        return bot.send_message(chat_id, content['errors']['ru']['something_went_wrong'])
    else:
        return bot.send_message(chat_id, msg)


def language_check(user_id):
    lang = Users.get(Users.user_id == user_id).language
    return lang

def region_check(user_id):
    region = Users.get(Users.user_id == user_id).region
    return region

def game_button(lang):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text=content['info_messages'][lang]['play_button']))

    return keyboard

def save_game_session(user_id, score, game_id):
    print('enter', user_id, score, game_id)
    game_session_query = GS(
        game_id = game_id,
        user_id = user_id,
        score = score
    )
    game_session_query.save()

    return


def set_nickname(user_id, name):
    try:
        if Users.select().where(Users.nickname == name).exists():
            return content['errors'][language_check(user_id)]['nickname_already_exists']
        user_query = Users.get(Users.user_id == user_id)
        user_query.nickname = name
        user_query.save()
        return ''
    except Exception as err:
        print(err)
        return 'err'

def set_language(user_id, lang):
    try:
        user_query = Users.get(Users.user_id == user_id)
        user_query.language = lang.split('_')[0]
        user_query.save()
        return False
    except Exception as err:
        print(err)
        return True

def set_region(user_id, region):
    try:
        user_query = Users.get(Users.user_id == user_id)
        user_query.region = region.split('_')[0]
        user_query.save()
        return False
    except Exception as err:
        print(err)
        return True

