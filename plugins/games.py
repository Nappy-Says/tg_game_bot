import json
from peewee import fn
from utils import language_check, game_button
from telebot import TeleBot, types
from models.games import Games, GamesSession as GS

with open("configs/cfg.json") as jsonFile:
    config = json.load(jsonFile)
    jsonFile.close()

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()

games_dict = config['games']

def list_of_games(msg: types.Message, bot: TeleBot):
    lang = language_check(msg.from_user.id)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*games_dict.keys(), row_width=2)

    bot.send_message(msg.chat.id, content['info_messages'][lang]['chooise_game'], reply_markup=keyboard)


def games_text_handler(msg: types.Message, bot: TeleBot):
    lang = language_check(msg.from_user.id)
    if msg.text in games_dict.keys():
        bot.send_message(msg.chat.id, content['info_messages'][lang]['good_luck'], reply_markup=game_button(lang))
        bot.send_game(msg.chat.id, game_short_name=games_dict[msg.text])

    if msg.text == '🎮 Сыграть' or msg.text == '🎮 Ойнау' or msg.text == "🎮 Ойнау":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*games_dict.keys(), row_width=2)

        bot.send_message(msg.chat.id, content['info_messages'][lang]['chooise_game'], reply_markup=markup)


def open_game(query, bot):
    print(query)
    game_query = Games.get(Games.short_name == query.game_short_name)
    high_score = GS.select(fn.MAX(GS.score)).where(GS.user_id == query.from_user.id, GS.game_id == game_query.id).scalar()

    if high_score is None:
        high_score = 0

    gameURL = config['url_prefix'] + f"/{query.game_short_name}/?uid={query.from_user.id}&mid={query.message.id}&cid={query.message.chat.id}&gid={game_query.id}&hs={high_score}"
    bot.answer_callback_query(query.id, url=gameURL)
