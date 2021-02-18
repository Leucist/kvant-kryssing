import telebot
from telebot.apihelper import ApiException

import config
import json

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

countries = ["Латвия", "Польша(недоступно)", "Литва(недоступно)"]
methods = ['Имя', 'Фамилия', 'Годы жизни']
adm_functions = ['Рассылка', 'Провести опрос', 'Просмотреть БД']
personal_data = {}


# language_code можно использовать для определения языка~
# возможность вмешаться в разговор с помощью консоли? Вряд ли - через серв. Ака экстренное соо о работах или updt
# json.loads(data_base.write()) 0_o (?)
# def decision(func):
#     def wrapped(*args, **kwargs):
#         func(*args, **kwargs)
#         before_taking_decision(*args, **kwargs)
#     return wrapped
#
#
# def taking_decision(*args, **kwargs):
#     if args[0].text == "Да":
#         return True
#     elif args[0].text == "Нет":
#         return False
#
# # декоратор над декоратором? Почему бы и нет()
# def before_taking_decision(*args, **kwargs):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton("Да")
#     item2 = types.KeyboardButton("Нет")
#     markup.add(item1, item2)
#     sent = bot.send_message(args[0].chat.id, "Принято.\nНачинаем поиск?", reply_markup=markup)
#     bot.register_next_step_handler(sent, taking_decision)
#     return before_taking_decision


@bot.message_handler(commands=['start'])
def start(message):
    sticker = open('static/welcome.tgs', 'rb')
    Person(message).initialisation()
    markup = back_markup()
    bot.send_sticker(message.chat.id, sticker)
    bot.send_message(message.chat.id,
                     "Здравствуй, {0.first_name}!\nЯ - <b>{1.first_name}</b>, чат-бот, который создан, чтобы помогать людям!".format(
                         message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == 1064282294:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for function in adm_functions:
            item = types.KeyboardButton(function)
            markup.add(item)
        item = types.KeyboardButton("Назад ➤")
        markup.add(item)
        sent = bot.send_message(message.chat.id, "Что бы Вы хотели сделать?", reply_markup=markup)
        bot.register_next_step_handler(sent, admin_after)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.")


def admin_after(message):
    markup = back_markup()
    if message.from_user.id == 1064282294:
        if message.text == "Рассылка":
            sent = bot.send_message(message.chat.id, "Какое сообщение Вы хотите разослать?")
            bot.register_next_step_handler(sent, mailing)
        elif message.text == "Просмотреть БД":
            Person(message).show_database()
        elif message.text == 'Провести опрос':
            sent = bot.send_message(message.chat.id, "Опрос на какую тему Вы хотите провести?")
            bot.register_next_step_handler(sent, mailing, arguments=True)
        elif message.text == "Назад ➤":
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У Вас недостаточно прав для использования этой функции.",
                         reply_markup=markup)


@bot.message_handler(content_types=['text'])
def chat(message):
    sticker = open('static/welcome.tgs', 'rb')
    error_stick = open('static/error.tgs', 'rb')
    Person(message).initialisation()  # каждый раз. Сделать это счастье на один раз не выходит пока
    # keyboard
    markup = back_markup()
    if message.chat.type == 'private':
        # if message.from_user.id == 1064282294:
        if message.text.lower() == 'привет':
            bot.send_sticker(message.chat.id, sticker)
            bot.send_message(message.chat.id,
                             "Здравствуй, {0.first_name}!\nЯ - <b>{1.first_name}</b>, чат-бот, который создан, чтобы помогать людям!".format(
                                 message.from_user, bot.get_me()), parse_mode='html', reply_markup=markup)

        elif message.text == 'Что ты умеешь?':
            bot.send_message(message.chat.id,
                             'Я могу помочь Вам восстановить своё генеалогическое древо, найти свои европейские корни (при их наличии), их упоминания в архивах.')
            bot.send_message(message.chat.id, 'Для начала работы нажмите на кнопку "Помоги мне 🔍" внизу ↓')

        elif message.text == 'Помоги мне 🔍':
            markup = types.ReplyKeyboardMarkup(row_width=0.1)
            item1 = types.KeyboardButton("Далее")
            for method in methods:
                item = types.KeyboardButton(method)
                markup.add(item)
            item2 = types.KeyboardButton("Назад ➤")
            markup.add(item1, item2)

            bot.send_message(message.chat.id, 'Хорошо, давайте начнем! По какому критерию Вы собираетесь искать?',
                             reply_markup=markup)

        elif message.text == 'Назад ➤':
            markup = back_markup()
            bot.send_message(message.chat.id, "Принято.", reply_markup=markup)

        elif message.text.lower() == 'далее' or message.text.lower() == 'дальше':
            markup = types.ReplyKeyboardMarkup(row_width=0.1)
            for country in countries:
                item = types.KeyboardButton(country)
                markup.add(item)
            item = types.KeyboardButton("Назад ➤")
            markup.add(item)
            sent = bot.send_message(message.chat.id, "Выберите страну, в которой будет осуществлен поиск",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, country_chose, personal_data)

        elif message.text == 'Пополнить баланс':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("2.99$")
            item2 = types.KeyboardButton("Назад ➤")
            markup.add(item1, item2)
            sent = bot.send_message(message.chat.id, "На какую сумму Вы хотите пополнить баланс?",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, pre_transactions)

        else:
            for method in methods:
                if message.text == method:
                    bot.send_message(message.chat.id, "(Данные следует вводить на родном языке)")
                    bot.send_message(message.chat.id,
                                     "(Примерные годы жизни следует вводить в формате XXXX-XXXX (прим.: 1800-1900))")
                    sent = bot.send_message(message.chat.id, method + " искомой личности:")
                    bot.register_next_step_handler(sent, receiving_data, method)
                    break

            else:
                markup = back_markup()
                bot.send_sticker(message.chat.id, error_stick)
                bot.send_message(message.chat.id,
                                 'Я никак не могу Вас понять. Нажмите на одну из кнопок и следуйте инструкциям!',
                                 reply_markup=markup)
        # else:  # на время разработки
        #     bot.send_sticker(message.chat.id, sticker)
        #     bot.send_message(message.chat.id, "Привет!")
        #     bot.send_message(message.chat.id,
        #                      "Данный бот сейчас находится на стадии доработки, так что его функции временно заморожены." +
        #                      "\nПопробуйте позже :)")


def country_chose(message, personal_data):
    for country in countries:
        if message.text == country:
            if country == 'Латвия':
                c = 'LVA'
            elif country == 'Польша':
                c = 'POL'
            elif country == 'Литва':
                c = 'LTU'
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("Да")
            item2 = types.KeyboardButton("Нет")
            markup.add(item1, item2)
            sent = bot.send_message(message.chat.id, "Принято.\nНачинаем поиск?", reply_markup=markup)
            bot.register_next_step_handler(sent, search, personal_data, c)


def receiving_data(message, method):
    personal_data[method] = message.text
    bot.send_message(message.chat.id, 'Принято.\nЧтобы изменить ' + method.lower() + ' просто нажмите "' + method +
                     '" еще раз.\nЗнаете другую информацию? Тогда нажмите на другую кнопку↓\nЕсли это все, напишите "Далее"')


def search(message, personal_data, country):  # проверить все нахрен
    error_stick = open('static/error.tgs', 'rb')
    result = []
    if message.text == "Да":
        if country == "LVA":
            for var in range(1):  # +костыль()
                with open("LVA-archive.json", "r", encoding="UTF-8") as source_file:
                    data = json.loads(source_file.read())
                    if "Годы жизни" in personal_data:
                        try:
                            first = int(personal_data["Годы жизни"][:4])
                            last = int(personal_data["Годы жизни"][5:])
                        except ValueError:
                            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                            item = types.KeyboardButton("Назад ➤")
                            markup.add(item)
                            bot.send_sticker(message.chat.id, error_stick)
                            bot.send_message(message.chat.id,
                                             "Допущена ошибка при вводе данных.\nГоды жизни введены неверно (Неверный формат).\n" +
                                             "(Примерные годы жизни следует вводить в формате XXXX-XXXX (прим.: 1800-1900))",
                                             reply_markup=markup)
                            break
                    for j in range(len(data)):
                        for i in data['item' + str(j)]:
                            variable = 0
                            try:
                                bdate = int(i["Дата рождения"][:4])
                            except ValueError:
                                bdate = 0
                            for key1 in personal_data:
                                for key2 in i:
                                    if key1 == key2:
                                        try:
                                            if personal_data[key1] == i[key1] and (
                                                    first <= bdate <= last or bdate == 0):
                                                variable += 1
                                                for key in i:
                                                    if i[key] == " ":
                                                        i[key] = "Не указано."
                                            else:
                                                variable -= 1
                                        except UnboundLocalError:
                                            if personal_data[key1] == i[key1]:
                                                variable += 1
                                                for key in i:
                                                    if i[key] == " ":
                                                        i[key] = "Не указано."
                                            else:
                                                variable -= 1
                                        break
                            if variable > 0:
                                result.append(i)
                    Person(message).search_made(0)
                    if not result:
                        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        item = types.KeyboardButton("Назад ➤")
                        markup.add(item)
                        bot.send_message(message.chat.id,
                                         "Ничего не найдено.\nВозможно, данных о таком человеке не существует или допущена ошибка во введенных данных.",
                                         reply_markup=markup)
                    else:
                        # money = Person(message).transactions(0)
                        # if money >= 2.99:
                        Person(message).search_made(1)
                        #     Person(message).transactions(-1, 2.99)
                        bot.send_message(message.chat.id, "Вот список возможных людей, которых Вы ищете:",
                                         reply_markup=None)
                        variable = 0
                        with open("s-results/result" + str(message.from_user.id) + ".txt", "w",
                                  encoding='UTF-8') as result_file:
                            for i in result:
                                variable += 1
                                result_file.write(str(variable) + ') ' + "\nИмя: " + i['Имя'] + "\nФамилия: " + i[
                                    'Фамилия'] + "\nОтчество: " + i['Отчество'] + "\nДата рождения: " + i[
                                                      'Дата рождения'] + "\nМесто рождения: " + i[
                                                      'Место рождения'] + "\nМесто приписки: " + i[
                                                      'Место приписки'] + '\n\n')
                        with open("s-results/result" + str(message.from_user.id) + ".txt", "r",
                                  encoding='UTF-8') as result_file:
                            bot.send_document(message.chat.id, result_file)
                            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                            item = types.KeyboardButton("Назад ➤")
                            markup.add(item)
                            bot.send_message(message.chat.id, "Файл с результатом Вашего поиска.",
                                             reply_markup=markup)
                        # else:
                        #     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                        #     item1 = types.KeyboardButton("Пополнить баланс")
                        #     item2 = types.KeyboardButton("Назад ➤")
                        #     markup.add(item1, item2)
                        #     bot.send_message(message.chat.id,
                        #                      "По Вашему запросу был найден результат.\nОднако на Вашем счету недостаточно средств, чтобы просмотреть его.\n" +
                        #                      'Напишите "Пополнить баланс" или нажмите на одну из кнопок ниже для того, чтобы пополнить баланс.'
                        #                      + "\nНа Вашем счету не хватает " + str(2.99 - money)[:4] + "$",
                        #                      reply_markup=markup)
        elif country == "POL" or country == "LTU":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item = types.KeyboardButton("Назад ➤")
            markup.add(item)
            bot.send_message(message.chat.id, "К сожалению, поиск в архивах данных государств еще не доступен.",
                             reply_markup=markup)
    elif message.text == "Нет":
        markup = back_markup()
        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)


def database_write(data):
    with open("data_base.json", "w", encoding="UTF-8") as database:
        json.dump(data, database, indent=1, ensure_ascii=False, separators=(',', ':'))


class Person:
    def __init__(self, message):
        self.message = message
        self.pid = message.from_user
        self.id_number = self.pid.id
        # self.database_read = open("data_base.json", "r", encoding="UTF-8")
        # self.data = json.loads(self.database_read.read())

    def initialisation(self):
        all_data = {}
        with open("data_base.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            for i in data['users']:
                if i['id'] == self.id_number:
                    break
            else:
                amount = int(data['items']) + 1
                data = data['users']
                user = {"id": self.id_number, "first_name": self.pid.first_name, "last_name": self.pid.last_name,
                        "username": self.pid.username, "money": 0, "search_count": 0, "search_count_success": 0,
                        "is_bot": self.pid.is_bot}
                data.append(user)
                all_data['items'] = amount
                all_data['users'] = data
                database_write(all_data)

    def show_database(self):
        try:
            with open("data_base.json", "r", encoding="UTF-8") as database_file:
                bot.send_document(self.message.chat.id, database_file)
        except FileNotFoundError:
            bot.send_message(self.message.chat.id, "[Ошибка] Файл БД не найден.", reply_markup=None)

    def transactions(self, *args):
        direction = args[0]
        try:
            amount = args[1]
        except IndexError:
            pass
        with open("data_base.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            for i in data['users']:
                if i['id'] == self.id_number:
                    if direction == 1:  # Добавить/положить
                        pass  # Нужно прикрутить оплату
                    elif direction == -1:  # Потратить/снять
                        i['money'] = i['money'] - amount
                    elif direction == 0:  # Проверить счет
                        return i['money']
                    database_write(data)
                    # bot.send_message(self.message.chat.id, "У Вас на счету " + str(i['money']) + "$")

    def search_made(self, variable):
        with open("data_base.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            for i in data['users']:
                if i['id'] == self.id_number:
                    if variable == 0:
                        i['search_count'] += 1
                    elif variable == 1:
                        i['search_count_success'] += 1
                    database_write(data)

    ########### useless ####### we need to use it ################################################
    def database(self):
        with open("data_base.json", "r", encoding="UTF-8") as database:
            data = json.loads(database.read())
            for i in data['users']:
                if i['id'] == self.id_number:
                    return data, i
            else:
                return data


##############################################################################################


def mailing(message, arguments=None):
    markup = back_markup()
    if message.text == "Назад ➤":
        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
        return -1
    with open("data_base.json", "r", encoding="UTF-8") as database:
        data = json.loads(database.read())
        if arguments:
            for person in data['users']:
                try:
                    if person['id'] != message.from_user.id:
                        sent = bot.send_message(person['id'], message.text, reply_markup=markup)
                        bot.register_next_step_handler(sent, feedback, message.text)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            return 0
        if message.content_type == 'text':
            for person in data['users']:
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_message(person['id'], message.text, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    continue
                else:
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'photo':
            raw = message.photo[2].file_id
            name = "mailing.jpg"
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as photo:
                photo.write(downloaded_file)
            for person in data['users']:
                photo = open(name, "rb")
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_photo(person['id'], photo, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    photo.close()
                    continue
                else:
                    photo.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        elif message.content_type == 'document':
            raw = message.document.file_id
            name = "mailing" + message.document.file_name[-4:]
            file_info = bot.get_file(raw)
            downloaded_file = bot.download_file(file_info.file_path)
            with open(name, "wb") as document:
                document.write(downloaded_file)
            for person in data['users']:
                document = open(name, "rb")
                try:
                    if person['id'] != message.from_user.id:
                        bot.send_document(person['id'], document, reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, "Принято.", reply_markup=markup)
                except ApiException:
                    document.close()
                    continue
                else:
                    document.close()
                    continue
            bot.send_message(message.chat.id, "Разослано.", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Неподдерживаемый тип файла", reply_markup=markup)


def feedback(message, question):
    bot.send_message(1064282294,
                     'Ответ на Ваш вопрос "' + question + '" — "' + message.text + '" от:\n(id) ' + str(message.from_user.id) + ',\n(name) '
                     + str(message.from_user.first_name))
    bot.send_message(message.chat.id, "Принято.\nБлагодарим за ответ!)")


def pre_transactions(message):
    input_amount = message.text
    try:
        amount = float(input_amount)
        bot.send_message(message.chat.id, "Принято.")
        # Person(message).transactions(1, amount)
    except ValueError:
        amount = ""
        chars = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, '.']  # '.' и ',' — для float(?)
        for i in input_amount:
            try:
                i = int(i)
            except ValueError:
                pass
            for j in range(len(chars)):
                if i == chars[j]:
                    amount = amount + str(i)
                elif i == ',':
                    amount = amount + '.'
                    break
        try:
            amount = float(amount)
            bot.send_message(message.chat.id, "Принято.")
            # Person(message).transactions(1, amount)
        except ValueError:
            bot.send_message(message.chat.id, "Некорректное значение суммы.\nПопробуйте ещё раз.")
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            item1 = types.KeyboardButton("2.99$")
            item2 = types.KeyboardButton("Назад ➤")
            markup.add(item1, item2)  # Он все принимает это за словарь, я хз, что с ним.
            sent = bot.send_message(message.chat.id, "На какую сумму Вы хотите пополнить баланс?",
                                    reply_markup=markup)
            bot.register_next_step_handler(sent, pre_transactions)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Да")
    item2 = types.KeyboardButton("Нет")
    markup.add(item1, item2)
    sent = bot.send_message(message.chat.id,
                            "Вы уверены, что хотите пополнить свой баланс на " + str(amount) + "$?",
                            reply_markup=markup)
    bot.register_next_step_handler(sent, decision, amount)


def decision(message, amount):
    if message.text == "Да":
        bot.send_message(message.chat.id, "Принято.")
        Person(message).transactions(1, amount)
    elif message.text == "Нет":
        bot.send_message(message.chat.id, "Принято.")


def back_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Что ты умеешь?")
    item2 = types.KeyboardButton("Помоги мне 🔍")
    markup.add(item1, item2)
    return markup


def compose_letter():
    pass


bot.polling(none_stop=True)
