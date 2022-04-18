import logging
import random
import config
from telegram import Update, ForceReply, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler
from datetime import datetime
from requests import get, post, put

d1 = {'LINKS': None, 'TEXT': None, 'THEME_NOW': None, 'changed': None, 'name': None}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def check(update: Update, arg=1):
    if len(update.message.text.split()) > 1:
        return 1
    if arg:
        update.message.reply_text('в команде должны быть указаны необходимые параметры /help')
    return 0


def close_keyboard(update, context):
    update.message.reply_text(
        "Ok",
        reply_markup=ReplyKeyboardRemove()
    )


def help(update: Update, context: CallbackContext):
    answer = """/start
    /set_name <новое имя> поменять имя
    /add_theme <название темы> добавление темы, в темы можно добавлять заметки
    /get_all_themes просмотреть свои темы
    /rename_theme <новое название> выберите заметку которую хотитн переназвать
    /get_notes будут показны темы, нажав на них, вы узнаете заметки в выбраной теме
    /add_note <название заметки> будут показны темы, нажав на них, вы сможете добавить заметку
    /del_theme <удалить тему> все её заметки будут перенесены в тема 'всякое'
    """
    update.message.reply_text(answer)


def bot_started(update: Update, context: CallbackContext):
    agree = KeyboardButton("отправить номер", request_contact=True)
    s1 = [[agree]]
    markup = ReplyKeyboardMarkup(s1)
    update.message.reply_text(f"""чтобы создать или привязать аккаунт на сайте ARZETEL разрешите 
    использовать ваш номер, /help поможет осмоиться ботом""", reply_markup=markup)


def take_nomer(update: Update, context: CallbackContext):
    contact = update.message.contact
    name = contact.first_name
    nomer = contact.phone_number
    request = 'api/user_add'
    res = post(config.address + request, json={'name': name, 'nomer': nomer,
                                               'tele_id': update.effective_user.id})
    update.message.reply_text(name + ' ' + nomer)


def set_name(update: Update, context: CallbackContext):
    if not check(update):
        return 0
    message = ' '.join(update.message.text.split()[1:])
    requset = 'api/user_set_name'
    res = post(config.address + requset, json={'new_name': message,
                                               'id': update.effective_user.id})
    update.message.reply_text(f'имя измененно на {message}')


def get_themes(update: Update, context: CallbackContext):
    id = update.effective_user.id
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    s = ''
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        s += get(config.address + req2).json()['answer'] + '\n'
    update.message.reply_text(f"""{s}""")


def add_theme(update: Update, context: CallbackContext):
    if not check(update):
        return 0
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/theme_add/'
    res = post(config.address + req, json={'header': message, 'user_id': id})
    update.message.reply_text(f'добавлена тема {message}')


def rename_theme(update: Update, context: CallbackContext):
    if not check(update):
        return 0
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/retheme {bt_text} && {message}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('переназвать', reply_markup=markup)


def retheme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    old, new = ' '.join(update.message.text.split()[1:]).split('& ')
    old = old[:-2]
    req = 'api/id_from_header/'
    id = str(get(config.address + req + f'/{id}/{old}').json()['answer'])
    if not id.isdigit():
        raise AttributeError("LOH")
    req2 = 'api/set_theme_header'
    res = put(config.address + req2, json={'id': id, 'header': new})
    update.message.reply_text(res.json()['answer'])


def any_text(update: Update, context: CallbackContext):
    message = update.message.text
    if message == 'отменить':
        close_keyboard(update, context)
        return 0
    if d1["LINKS"]:
        id = d1["LINKS"]
        user_id = update.effective_user.id
        req = f'api/add_links'
        link = update.message.text
        res = post(config.address + req, json={'id': id, 'new_links': link, 'user_id': user_id})
        d1['LINKS'] = None
        update.message.reply_text('ссылка добавлена')
        return 0
    if d1["TEXT"]:
        id = d1['TEXT']
        req = f'api/set_texts'
        txt = update.message.text
        res = post(config.address + req, json={'id': id, 'new_text': txt})
        d1['TEXT'] = None
        update.message.reply_text('текст изменён')
        return 0
    if d1['name']:
        id = d1['name']
        req = 'api/set_note_header'
        txt = update.message.text
        res = post(config.address + req, json={'id': id, 'new_header': txt})
        d1['name'] = None
        update.message.reply_text('название изменёно')
        return 0


def delete_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):

        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        if bt_text != 'всякое':
            reply.append([KeyboardButton(f'/delete_theme {bt_text}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('удалить', reply_markup=markup)


def del_theme(update: Update, context: CallbackContext):
    if not check(update):
        return 0
    message = ' '.join(update.message.text.split()[1:])
    user_id = update.effective_user.id
    req = 'api/del_theme'
    req2 = f'api/id_from_header/{user_id}/{message}'
    id = get(config.address + req2).json()['answer']
    res = post(config.address + req, json={'user_id': user_id, 'id': id})
    update.message.reply_text(res.json()['answer'])


def add_note(update: Update, context: CallbackContext):
    if not check(update):
        return 0
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/add_note_to_theme {bt_text} && {message}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('добавить', reply_markup=markup)


def add_note_to_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    old, new = ' '.join(update.message.text.split()[1:]).split('& ')
    old = old[:-2]
    req = 'api/id_from_header'
    id = str(get(config.address + req + f'/{id}/{old}').json()['answer'])
    if not id.isdigit():
        raise AttributeError("LOH")
    req2 = 'api/add_note'
    res = post(config.address + req2, json={'theme_id': id, 'header': new})
    reply = []
    b1 = KeyboardButton(f'/add_links_to_note {old} && {new}')
    b2 = KeyboardButton(f'/add_text_to_note {old} && {new}')
    b3 = KeyboardButton(f'отменить')
    reply.append([b1])
    reply.append([b2])
    reply.append([b3])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text(text='в заметку добавить', reply_markup=markup)


def get_notes_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    reply = [['отменить']]
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        reply.append([KeyboardButton(f'/get_note_from_theme {bt_text}')])
    markup = ReplyKeyboardMarkup(reply)
    update.message.reply_text('выбрать', reply_markup=markup)


def get_notes(update: Update, context: CallbackContext):
    if not check(update):
        return 0
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = 'api/id_from_header/'
    theme_id = get(config.address + req + f'/{id}/{message}').json()['answer']
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/user_get_notes/{theme_id}'
    res = get(config.address + req2).json()['answer']
    reply = [['отменить']]

    for i in range(len(res) // 3):
        reply.append(
            [KeyboardButton(f'/show_note {res[i]}'),
             KeyboardButton(f'/show_note {res[len(res) // 3 + i]}'),
             KeyboardButton(f'/show_note {res[len(res) // 3 * 2 + i]}')])
    markup = ReplyKeyboardMarkup(reply)
    d1['THEME_NOW'] = theme_id
    update.message.reply_text('заметки', reply_markup=markup)


def add_links_to_note(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    message = context.args
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{userid}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note[2:]}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    d1['LINKS'] = note_id
    update.message.reply_text('напишите название ссылки')


def add_text_to_note(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    message = update.message.text.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{userid}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note[2:]}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    d1['TEXT'] = note_id
    update.message.reply_text('напишите текст ссылки')


def show_note(update: Update, context: CallbackContext):
    if not check(update, 0):
        update.message.reply_text('используйте через /get_notes')
        return 0
    note = ' '.join(update.message.text.split()[1:])
    theme_id = d1['THEME_NOW']
    req2 = f'api/get_id_note/{note}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    if not note_id.isdigit():
        raise AttributeError("LOH")
    req = f'api/note_text/{note_id}'
    text = get(config.address + req).json()['answer']
    req3 = f'api/note_links/{note_id}'
    links = get(config.address + req3).json()['answer']
    req4 = f'api/note_get_theme/{note_id}'
    theme = get(config.address + req4).json()['answer']
    reply = [['отменить']]
    b1 = KeyboardButton(f'/add_links_to_note {theme} && {note}')
    b2 = KeyboardButton(f'/set_text_to_note {theme} && {note}')
    b3 = KeyboardButton(f'/set_name_to_note {theme} && {note}')
    b4 = KeyboardButton(f'/del_note {theme} && {note}')
    reply.append([b1])
    reply.append([b2])
    reply.append([b3])
    reply.append([b4])
    markup = ReplyKeyboardMarkup(reply)
    send_message = update.message.reply_text(
        f"""название - {note} \n тема - {theme} \n текст - {text} \n ссылки -{links} """,
        reply_markup=markup)
    d1['changed'] = send_message.message_id


def set_name_to_note(update: Update, context: CallbackContext):
    userid = update.effective_user.id
    message = update.message.text.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{userid}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note[2:]}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    print(note_id)
    d1['name'] = note_id
    update.message.reply_text('напишите новое название')


def del_note(update: Update, context: CallbackContext):
    if not check(update, 0):
        update.message.reply_text('используйте через /get_notes')
        return 0
    userid = update.effective_user.id
    message = update.message.text.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{userid}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note[2:]}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    req = 'api/del_note'
    res = post(config.address + req, json={'id': note_id}).json()['answer']
    update.message.reply_text(res)


def main():
    updater = Updater(config.TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.contact, take_nomer))
    dispatcher.add_handler(CommandHandler("start", bot_started))
    dispatcher.add_handler(CommandHandler('set_name', set_name))
    dispatcher.add_handler(CommandHandler('add_theme', add_theme))
    dispatcher.add_handler(CommandHandler('get_all_themes', get_themes))
    dispatcher.add_handler(CommandHandler('rename_theme', rename_theme))
    dispatcher.add_handler(CommandHandler('retheme', retheme))
    dispatcher.add_handler(CommandHandler('del_theme', delete_theme))
    dispatcher.add_handler(CommandHandler('delete_theme', del_theme))
    dispatcher.add_handler(CommandHandler('add_note', add_note))
    dispatcher.add_handler(CommandHandler('add_note_to_theme', add_note_to_theme))
    dispatcher.add_handler(CommandHandler('get_notes', get_notes_theme))
    dispatcher.add_handler(CommandHandler('get_note_from_theme', get_notes))
    dispatcher.add_handler(CommandHandler('add_links_to_note', add_links_to_note))
    dispatcher.add_handler(CommandHandler('add_text_to_note', add_text_to_note))
    dispatcher.add_handler(CommandHandler('set_text_to_note', add_text_to_note))
    dispatcher.add_handler(CommandHandler('set_name_to_note', set_name_to_note))
    dispatcher.add_handler(CommandHandler('del_note', del_note))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('h', help))
    dispatcher.add_handler(CommandHandler('show_note', show_note))
    dispatcher.add_handler(MessageHandler(Filters.text, any_text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
