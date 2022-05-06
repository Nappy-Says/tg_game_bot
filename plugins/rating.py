import json

from models.mod import db
from models.users import Users
from telebot import TeleBot, types
from utils import language_check, send_error
from models.games import Games, GamesSession as GS
from telegram import Game, InlineKeyboardButton, InlineKeyboardMarkup

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()

with open("configs/cfg.json") as jsonFile:
    config = json.load(jsonFile)
    jsonFile.close()

games_dict = config['games']

def rating_show(msg: types.Message, bot: TeleBot):
    lang = language_check(msg.json['chat']['id'])
    temp_content = content['rating'][lang]

    reply_markup = InlineKeyboardMarkup(
        [ [InlineKeyboardButton(k, callback_data='rating|' + v)] for k, v in games_dict.items() ]
    ).to_json()

    bot.send_message(msg.from_user.id, temp_content['message'], reply_markup=reply_markup)


def callback_rating_games(query: types.CallbackQuery, bot: TeleBot):
    short_name = query.data.split('|')[1]
    lang = language_check(query.from_user.id)
    game_query = Games.select().where(Games.short_name == short_name)

    if not game_query.exists():
        send_error(query.from_user.id, bot)
        return
    
    query_game_sessions = db.execute_sql(f'''SELECT users.user_id, users.nickname, max(gs.score)
        FROM users
        INNER JOIN gamessession as gs
            ON gs.user_id = users.user_id
        WHERE gs.game_id = {game_query.get().id}
        GROUP BY users.user_id
        ORDER BY gs.score DESC
        LIMIT 10;
    ''')

    game_sessions = query_game_sessions.fetchall()

    if len(game_sessions) == 0:
        bot.send_message(query.from_user.id, content['errors'][lang]['no_game_sessions_yet'])
        return

    text = content['rating'][lang]['top10'].format(name_of_game = game_query.get().name)
    for i in range(len(game_sessions)):
        if game_sessions[i][0] == query.from_user.id:
            text += '<b>' + str(i+1) + f'. {game_sessions[i][1]} — {game_sessions[i][2]}</b>\n'
            continue

        text += str(i+1) + f'. {game_sessions[i][1]} — {game_sessions[i][2]}\n'

    bot.send_message(query.from_user.id, text, parse_mode='html')
