import json
import random
import string
import logging
from models.users import Users
from telebot import TeleBot, types
from utils import language_check, game_button

with open("configs/content.json") as jsonFile:
    content = json.load(jsonFile)
    jsonFile.close()


def save_user_to_database(data: types.Message):
    try:
        _user_id = data.from_user.id
        _username = data.from_user.username
        _first_name = data.from_user.first_name
        _last_name = data.from_user.last_name

        # If the user has ever launched a bot, but has not been registered, 
        # then we repeat the registration process. Otherwise, we issue 
        # re-registration information.
        if Users.select().where(Users.user_id == _user_id).exists():
            if Users.select().where(Users.user_id == _user_id, Users.is_registered == True):
                return content['errors']['ru']['re_registration']
            return

        user = Users(
            user_id = _user_id,
            username = _username,
            first_name = _first_name,
            last_name = _last_name,
            nickname = 'Player_' + ''.join([random.choice(string.digits) for i in range(6)])
        )
        user.save()

        return
    except Exception as err:
        logging.error(err)
        print(err)
        return content['errors']['ru']['something_went_wrong']

def update_user_data(data: types.Message, region: str, lang: str):
    try:
        _user_id = data.from_user.id
        _phone = data.contact.phone_number

        user_query = Users.get(Users.user_id == _user_id)
        user_query.language = lang
        user_query.phone = _phone
        user_query.region = region
        user_query.is_registered = True
        user_query.save()

        print(user_query.language, user_query.phone, user_query.region)

        return '', ''
    except AttributeError as err:
        logging.error(err)
        print(err)
        return content['errors'][lang]['no_contact_data'], 'AttributeError'
    except Exception as err:
        logging.error(err)
        print(err)
        return content['errors'][lang]['something_went_wrong'], 'Exception'



def start_and_get_region(msg: types.Message, bot: TeleBot):
    err = save_user_to_database(msg)
    if err:
        lang = language_check(msg.from_user.id)
        bot.send_message(msg.chat.id, err, reply_markup=game_button(lang))
        return

    kazakhstan = types.KeyboardButton(text="🇰🇿 Қазақстан")
    uzbekistan = types.KeyboardButton(text="🇺🇿 O'zbekiston")

    country_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    country_keyboard.add(kazakhstan, uzbekistan, row_width=3)

    bot.send_message(msg.chat.id, "🇷🇺 Выберите страну\n🇰🇿 Елді таңдаңыз\n🇺🇿 Mamlakatni tanlang", reply_markup=country_keyboard)
    bot.register_next_step_handler(msg, get_lang, bot)


def get_lang(msg: types.Message, bot: TeleBot):
    russia = types.KeyboardButton(text="🇷🇺 Русский")
    kazakhstan = types.KeyboardButton(text="🇰🇿 Қазақ")
    uzbekistan = types.KeyboardButton(text="🇺🇿 О'zbek")

    region = msg.text
    lang_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)

    if region == '🇰🇿 Қазақстан':
        lang_keyboard.add(russia, kazakhstan, row_width=3)
        bot.send_message(msg.chat.id, '🇷🇺 Выберите язык\n🇰🇿 Тілді таңдаңыз', reply_markup=lang_keyboard)

    elif region == "🇺🇿 O'zbekiston":
        lang_keyboard.add(russia, uzbekistan, row_width=3)
        bot.send_message(msg.chat.id, '🇷🇺 Выберите язык\n🇺🇿 Tilni tanlang', reply_markup=lang_keyboard)

    else:
        print('enter to ')
        bot.send_message(msg.chat.id, content['errors']['ru']['wrong_chooise_country'])
        start_and_get_region(msg, bot)
        return

    bot.register_next_step_handler(msg, welcome_message, bot, content['lang_and_country'][region])


def welcome_message(msg: types.Message, bot: TeleBot, region: str):
    if msg.text not in content['lang_and_country'].keys():
        bot.send_message(msg.chat.id, content['errors']['ru']['wrong_chooise_country'])
        get_lang(msg, bot)
        return

    lang = content['lang_and_country'][msg.text]
    share_contact = types.KeyboardButton(text=content['start_message'][lang]['button'], request_contact=True)

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(share_contact)

    bot.send_message(msg.chat.id, content['start_message'][lang]['message'], reply_markup=keyboard)
    bot.register_next_step_handler(msg, get_contact, bot, region, lang)


def get_contact(msg: types.Message, bot: TeleBot, region: str, lang: str):
    err, tErrot = update_user_data(msg, region, lang)
    if err:
        if tErrot == 'AttributeError':
            bot.send_message(msg.chat.id, err)
            bot.register_next_step_handler(msg, get_contact, bot, region, lang)
            return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton(text="🎮 Сыграть"))
    
    bot.send_message(msg.chat.id, content['start_message'][lang]['successful_registration'], reply_markup=keyboard)
