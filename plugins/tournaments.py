from datetime import datetime
import json

from utils import language_check
from telebot import TeleBot, types
from utils import language_check, region_check
from models.games import GamesSession as GS, Tournaments as T
from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()


def tournaments_show(msg: types.Message, bot: TeleBot):
    region = region_check(msg.json['chat']['id'])
    lang = language_check(msg.json['chat']['id'])

    now = datetime.now()
    tours = T.select().where(T.country == region)

    plan = content['tournaments'][lang]['plan_tours']
    current = content['tournaments'][lang]['current_tours']

    buttons = []

    curr = plam = 1
    for i in tours:
        if i.date_of_start <= now:
            current += f'{curr}. {i.title}\n'
            buttons.append(InlineKeyboardButton(curr, callback_data=f'tour:{i.id}'))
            curr +=1
        if i.date_of_start >= now:
            plan += f'{plam}. {i.title}\n'
            plam += 1

    if plan == content['tournaments'][lang]['plan_tours']:
        plan += content['tournaments'][lang]['no_plan_tours']
    if current == content['tournaments'][lang]['current_tours']:
        current += content['tournaments'][lang]['no_current_tours']
    temp_content = current + '\n\n' + plan

    if msg.json['from']['id'] != msg.json['chat']['id']:
        bot.edit_message_text(temp_content, msg.json['chat']['id'], msg.id, reply_markup=InlineKeyboardMarkup([buttons]).to_json())
        return

    bot.send_message(msg.json['chat']['id'], temp_content, reply_markup=InlineKeyboardMarkup([buttons]).to_json(), parse_mode='html')


def callback_tournaments(query: CallbackQuery, bot: TeleBot):
    if query.data == 'tour:exit':
        tournaments_show(query.message, bot)
        return

    lang = language_check(query.from_user.id)
    tour_id = query.data.split(':')[1]

    tour = T.select().where(T.id == tour_id).get()
    message = content['tournaments'][lang]['more_about_tour'].format(name=tour.title, description=tour.content, start_date=tour.date_of_start.date(), end_date=tour.date_of_end.date(), game=tour.game.name)

    reply_markup = InlineKeyboardMarkup([
        [ InlineKeyboardButton(content['info_messages'][lang]['exit'], callback_data='tour:exit') ]
    ]).to_json()

    bot.edit_message_text(message, query.from_user.id, query.message.id, reply_markup=reply_markup)
