import re
import json
from peewee import fn
from models.users import Users
from telebot import TeleBot, types
from models.games import GamesSession as GS, Games as G
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils import language_check, set_language, send_error, set_nickname, set_region


with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()

list_of_commands = ['change_lang','change_region','change_nickname','reset_all_scores', 'profile_exit']


def get_me(msg: types.Message, bot: TeleBot):
    lang = language_check(msg.json['chat']['id'])
    temp_content = content['profile'][lang]
    user_query = Users.get(Users.user_id == msg.json['chat']['id'])
    games_sessions = (GS
        .select(fn.COUNT(GS.id))
        .where(GS.user_id == msg.json['chat']['id'])
    )

    xx = '—'
    ss = GS.select(GS.game_id, fn.COUNT(GS.game_id)).where(GS.user_id == msg.json['chat']['id']).group_by(GS.game_id).order_by(fn.COUNT(GS.game_id).desc()).limit(1)
    if ss.exists():
        xx = ss.get().game_id.name

    message = temp_content['message'].format(
        nick = user_query.nickname, 
        country = user_query.region,
        lang = user_query.language,
        favorite_game = xx,
        game_count = games_sessions.get()
    )

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(temp_content['menu']['change_lang'], callback_data="change_lang"),
                InlineKeyboardButton(temp_content['menu']['change_region'], callback_data="change_region")
            ],
            [
                InlineKeyboardButton(temp_content['menu']['change_nickname'], callback_data="change_nickname"),
                InlineKeyboardButton(temp_content['menu']['reset_all_scores'], callback_data="reset_all_scores")
            ]
        ]
    ).to_json()

    if msg.json['from']['id'] != msg.json['chat']['id']:
        bot.edit_message_text(message, chat_id=msg.json['chat']['id'], message_id=msg.message_id, reply_markup=reply_markup)
        return

    bot.send_message(msg.json['chat']['id'], message, reply_markup=reply_markup)


def callbacks_profile(query: types.CallbackQuery, bot: TeleBot):
    lang = language_check(query.from_user.id)
    temp_content = content['profile'][lang]

    if query.data == 'profile_exit':
        bot.clear_step_handler_by_chat_id(chat_id=query.message.chat.id)
        get_me(query.message, bot)
        return

    if query.data == 'change_lang':
        reply_markup = InlineKeyboardMarkup([
            [ InlineKeyboardButton(k, callback_data=v) for k, v in content['profile']['buttons']['langs'].items() ],
            [ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='profile_exit') ]
        ]).to_json()

        bot.edit_message_text(temp_content['chooise_lang'], message_id=query.message.message_id, chat_id=query.message.chat.id, reply_markup=reply_markup)

    if query.data == 'change_region':
        reply_markup = InlineKeyboardMarkup([
            [ InlineKeyboardButton(k, callback_data=v) for k, v in content['profile']['buttons']['regions'].items() ],
            [ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='profile_exit') ]
        ]).to_json()

        bot.edit_message_text(temp_content['chooise_lang'], message_id=query.message.message_id, chat_id=query.message.chat.id, reply_markup=reply_markup)

    if query.data == 'change_nickname':
        reply_markup = InlineKeyboardMarkup([
            [ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='profile_exit') ]
        ]).to_json()

        try:
            query = query.message
            message = bot.edit_message_text(temp_content['set_nickname'], message_id=query.json['message_id'], chat_id=query.json['chat']['id'], reply_markup=reply_markup)
            bot.register_next_step_handler(message, set_chooise_nickname, bot)
        except Exception as err:
            message = bot.send_message(query.json['chat']['id'], temp_content['set_nickname'], reply_markup=reply_markup)
            bot.register_next_step_handler(message, set_chooise_nickname, bot)




def set_chooise_nickname(msg: types.CallbackQuery, bot: TeleBot):
    lang = language_check(msg.from_user.id)
    if msg.content_type != 'text':
        send_error(msg.from_user.id, bot, content['errors'][lang]['wrong_nickname'])
        msg.data = 'change_nickname'
        callbacks_profile(msg, bot)
        return 
    print()

    if not bool(re.search('^(?!.*\.\.)(?!.*\.$)[^\W][\w.]{0,29}$', msg.text)):
        send_error(msg.from_user.id, bot, content['errors'][lang]['wrong_match_nickname'])
        msg.data = 'change_nickname'
        callbacks_profile(msg, bot)
        return 

    err = set_nickname(msg.json['chat']['id'], msg.text)
    if err != '':
        if err == 'err':
            send_error(msg.from_user.id, bot)
            msg.data = 'change_nickname'
            callbacks_profile(msg, bot)
            return
        send_error(msg.from_user.id, bot, err)
        msg.data = 'change_nickname'
        callbacks_profile(msg, bot)
        return

    reply_markup = InlineKeyboardMarkup([[ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='profile_exit') ]]).to_json()
    bot.send_message(msg.from_user.id, content['info_messages'][lang]['success'], reply_markup=reply_markup)



def set_chooise_language(query: types.CallbackQuery, bot: TeleBot):
    if set_language(query.from_user.id, query.data):
        send_error(query.from_user.id, bot)
        return

    lang = language_check(query.from_user.id)
    reply_markup = InlineKeyboardMarkup([[ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='profile_exit') ]]).to_json()
    bot.edit_message_text(content['info_messages'][lang]['success'], query.from_user.id, query.message.message_id, reply_markup=reply_markup)


def set_chooise_region(query: types.CallbackQuery, bot: TeleBot):
    if set_region(query.from_user.id, query.data):
        send_error(query.from_user.id, bot)
        return

    lang = language_check(query.from_user.id)
    reply_markup = InlineKeyboardMarkup([[ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='profile_exit') ]]).to_json()
    bot.edit_message_text(content['info_messages'][lang]['success'], query.from_user.id, query.message.message_id, reply_markup=reply_markup)
