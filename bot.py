import json
import telebot
import logging
from utils import *
from peewee import *
import plugins.auth as auth
import plugins.news as news
import plugins.menu as menu
import plugins.games as games
import plugins.rating as rating
import plugins.profile as profile
import plugins.tournaments as tournaments

logging.basicConfig(
    level=logging.ERROR,
    filename='configs/logs.log',
    format='[%(levelname)s] - %(asctime)s : %(message)s --> %(pathname)s:%(lineno)d'
)

with open("configs/cfg.json") as jsonFile:
    config = json.load(jsonFile)
    jsonFile.close()
with open("configs/content.json") as jsonFile2:
    content = json.load(jsonFile2)
    jsonFile2.close()

token = config['token']
bot = telebot.TeleBot(token)





@bot.callback_query_handler(func=lambda query: query)    
def callback_news(query):
    if query.message.content_type == 'game':
        games.open_game(query, bot)

    if query.data in profile.list_of_commands:
        profile.callbacks_profile(query, bot)
        return

    if query.data in ['ru_lang', 'kz_lang', 'uz_lang']:
        profile.set_chooise_language(query, bot)
        return

    if query.data in ['ru_region', 'kz_region', 'uz_region']:
        profile.set_chooise_region(query, bot)
        return

    try:
        tournaments_query = query.data.split(':')
        if len(tournaments_query) != 0:
            if tournaments_query[0] == 'tour':
                tournaments.callback_tournaments(query, bot)

        rating_query = query.data.split('|')
        if len(rating_query) != 0:
            if rating_query[0] == 'rating':
                rating.callback_rating_games(query, bot)


        news_query = query.data.split('_')
        if len(news_query) != 0:
            if news_query[0] == 'news':
                news.callback_get_news_by_id(query, bot)
    except Exception as err:
        print(err)
        pass

@bot.message_handler(commands=['rating'])
def show_rating(message):
    rating.rating_show(message, bot)

@bot.message_handler(commands=['tournaments'])
def all_tournaments(message):
    tournaments.tournaments_show(message, bot)

@bot.message_handler(commands=['news'])
def all_news(message):
    news.show_news(message, bot)


@bot.message_handler(commands=['menu'])
def main_menu(message):
    menu.show_menu(message, bot)


@bot.message_handler(commands=['profile'])
def user_profile(message):
    profile.get_me(message, bot)


@bot.message_handler(commands=['start'])
def start(message):
    auth.start_and_get_region(message, bot)


@bot.message_handler(commands=['games'])
def games_func(message):
    games.list_of_games(message, bot)


@bot.message_handler(content_types=['text'])
def text_handler(message):
    games.games_text_handler(message, bot)


def set_user_record(user_id, message_id, chat_id, score):
    try:
        bot.set_game_score(user_id=user_id, message_id=message_id, chat_id=chat_id, score=score, inline_message_id=1, force=True)
    except Exception as err:
        print(err)
        bot.send_message(chat_id, content['errors']['ru']['something_went_wrong'])

def tournament_push_notificate(game_name, country):
    try:
        for i in Users.select():
            if i.region == country:
                bot.send_message(i.user_id, content['tournaments'][i.language]['push_notification'].format(game=game_name), parse_mode='html')
    except Exception as err:
        print(err)

def push_notificate(message):
    try:
        for i in Users.select():
            bot.send_message(i.user_id, message,parse_mode='html')
    except Exception as err:
        print(err)



if __name__ == '__main__':
    logging.info('Bot is running successful!')
    print("Bot is running successful!")
    bot.infinity_polling()
