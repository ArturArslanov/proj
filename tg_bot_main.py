import logging
import random
import config
from telegram import Update, ForceReply, ReplyKeyboardRemove, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, \
    CallbackQueryHandler
from datetime import datetime
from requests import get, post, put

d1 = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


def create_inline_keybord(n, **kwargs):
    reply = []
    k = 0
    s1 = []
    for text, collback_quety in kwargs.items():
        s1.append(InlineKeyboardButton(text=text, callback_data=collback_quety))
        k += 1
        if not k % n:
            reply.append(s1)
            s1 = []
    if s1:
        reply.append(s1)
    markup = InlineKeyboardMarkup(reply)
    return markup


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
    answer = """/start"""
    s1 = {}
    s1['поменять имя'] = '/set_user_name'
    s1['просмотреть свои темы'] = '/get_all_themes'

    markup = create_inline_keybord(1, **s1)
    link = InlineKeyboardButton(text='перейти на сайт', url='http://127.0.0.1:8089/arzetel/')
    print(markup.inline_keyboard.append([link]))
    update.message.reply_text(answer, reply_markup=markup)


def bot_started(update: Update, context: CallbackContext):
    agree = KeyboardButton("отправить номер", request_contact=True)
    s1 = [[agree]]
    markup = ReplyKeyboardMarkup(s1)
    update.message.reply_text(f"""чтобы 
    создать или привязать аккаунт на сайте ARZETEL разрешите использовать ваш номер
    """, reply_markup=markup)


def add_d1(id):
    if id not in d1.keys():
        d1[id] = {'LINKS': None, 'TEXT': None, 'THEME_NOW': None, 'changed': None,
                  'name': None, 'add_theme_name': None, 'add_note_theme': None, 'set_name': None,
                  'register': None}


def take_nomer(update: Update, context: CallbackContext):
    add_d1(update.effective_user.id)
    contact = update.message.contact
    name = contact.first_name
    nomer = contact.phone_number
    request = 'api/user_add'
    res = post(config.address + request, json={'name': name, 'nomer': nomer,
                                               'tele_id': update.effective_user.id})
    if res.json()['answer'] == 'регистрация':
        update.message.reply_text('напишите пароль для регистрации')
        d1[update.effective_user.id]['register'] = True
        return 0
    help(update, context)


def set_name(id, message):
    requset = 'api/user_set_name'
    post(config.address + requset, json={'new_name': message,
                                         'id': id})
    return f'имя измененно на {message}'


def get_themes(id, con):
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    s1 = {}
    s1['добавить тему'] = f'/add_theme'
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        header = get(config.address + req2).json()['answer'] + '\n'
        s1[f'показать {header}'] = f'/get_note_from_theme {header}'
        s1[f'добавить в {header}'] = f'/add_note_to_theme {header}'
        s1[f'переназвать {header}'] = f'/rename_theme {header}'
        if 'всякое' not in header:
            s1[f'удалить {header}'] = f'/del_theme {header}'
    markup = create_inline_keybord(2, **s1)
    return 'что то', markup


def add_theme(id, message):
    req = f'api/theme_add/'
    post(config.address + req, json={'header': message, 'user_id': id})
    return f'добавлена тема {message}'


def retheme(id, message, theme):
    old, new = theme, message
    req = 'api/id_from_header/'

    id = str(get(config.address + req + f'/{id}/{old}').json()['answer'])
    if not id.isdigit():
        raise AttributeError("LOH")
    req2 = 'api/set_theme_header'
    res = put(config.address + req2, json={'id': id, 'header': new})
    return f'удачно переназвано с {old} на {new}'


def any_text(update: Update, context: CallbackContext):
    add_d1(update.effective_user.id)
    message = update.message.text
    if message == 'отменить':
        close_keyboard(update, context)
        return 0
    if d1[update.effective_user.id]["LINKS"]:
        id = d1[update.effective_user.id]["LINKS"]
        user_id = update.effective_user.id
        req = f'api/add_links'
        link = update.message.text
        post(config.address + req, json={'id': id, 'new_links': link, 'user_id': user_id})
        d1[update.effective_user.id]['LINKS'] = None
        update.message.reply_text('ссылка добавлена')
        return 0
    if d1[update.effective_user.id]["TEXT"]:
        id = d1[update.effective_user.id]['TEXT']
        req = f'api/set_texts'
        txt = update.message.text
        post(config.address + req, json={'id': id, 'new_text': txt})
        d1[update.effective_user.id]['TEXT'] = None
        update.message.reply_text('текст изменён')
        return 0
    if d1[update.effective_user.id]['name']:
        id = d1[update.effective_user.id]['name']
        req = 'api/set_note_header'
        txt = update.message.text
        post(config.address + req, json={'id': id, 'new_header': txt})
        d1[update.effective_user.id]['name'] = None
        update.message.reply_text('название изменёно')
        return 0
    if d1[update.effective_user.id]['add_theme_name']:
        add_theme(update.effective_user.id, message)
        d1[update.effective_user.id]['add_theme_name'] = None
        update.message.reply_text(f'добавлена тема {message}')
        return 0
    if d1[update.effective_user.id]['add_note_theme']:
        res, markup = add_note_to_theme(update.effective_user.id, message,
                                        d1[update.effective_user.id]['add_note_theme'])
        d1[update.effective_user.id]['add_note_theme'] = None
        update.message.reply_text(res, reply_markup=markup)
        return 0
    if d1[update.effective_user.id]['set_name']:
        res = set_name(update.effective_user.id, message)
        d1[update.effective_user.id]['set_name'] = None
        update.message.reply_text(res)
        return 0
    if d1[update.effective_user.id]['changed']:
        res = retheme(update.effective_user.id, message, d1[update.effective_user.id]['changed'])
        d1[update.effective_user.id]['changed'] = None
        update.message.reply_text(res)
        return 0
    if d1[update.effective_user.id]['register']:
        req = 'api/add_password/'
        res = post(config.address + req,
                   json={'user_id': update.effective_user.id, 'password': message})
        if res.json()['answer'] == 'ok':
            update.message.reply_text('вы успешно зарегестрировались')
            d1[update.effective_user.id]['register'] = None
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


def del_theme(id, con):
    message = ' '.join(con.data.split()[1:])
    user_id = id
    req = 'api/gdel_theme'
    req2 = f'api/id_from_header/{user_id}/{message}'
    id = get(config.address + req2).json()['answer']
    res = post(config.address + req, json={'user_id': user_id, 'id': id})
    return res.json()['answer']


def add_note_to_theme(id, message, theme):
    old, new = theme, message
    req = 'api/id_from_header'
    id = str(get(config.address + req + f'/{id}/{old}').json()['answer'])

    if not id.isdigit():
        raise AttributeError("LOH")
    req2 = 'api/add_note'
    post(config.address + req2, json={'theme_id': id, 'header': new})
    s1 = {}
    s1['добавить ссылку'] = f'/add_links_to_note {old} && {new}'
    s1['добавить текст'] = f'/add_text_to_note {old} && {new}'
    markup = create_inline_keybord(1, **s1)
    return f'в заметке {message}', markup


def get_notes_theme(update: Update, context: CallbackContext):
    id = update.effective_user.id
    message = ' '.join(update.message.text.split()[1:])
    req = f'api/user_get_themes/{id}'
    res = get(config.address + req).json()['answer']
    s1 = {}
    for i in range(len(res)):
        req2 = f'api/theme_header/{res[i]}'
        bt_text = get(config.address + req2).json()['answer']
        s1[bt_text] = f'/get_note_from_theme {bt_text}'
    markup = create_inline_keybord(3, **s1)
    update.message.reply_text('замекти какой темы?', reply_markup=markup)


def get_notes(id, con):
    message = ' '.join(con.data.split()[1:])
    req = 'api/id_from_header/'
    theme_id = get(config.address + req + f'/{id}/{message}').json()['answer']
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/user_get_notes/{theme_id}'
    res = get(config.address + req2).json()['answer']
    s1 = {}
    for i in res:
        s1[i] = f'/show_note {i}'
    markup = create_inline_keybord(3, **s1)
    d1[id]['THEME_NOW'] = theme_id
    return f'заметки темы {message}', markup


def add_links_to_note(id, con):
    message = con.data.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    note = note[2:]
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{id}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    d1[id]['LINKS'] = note_id
    return 'напишите название ссылки'


def add_text_to_note(id, con):
    message = con.data.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    note = note[2:]
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{id}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    d1[id]['TEXT'] = note_id
    return 'напишите текст ссылки'


def show_note(id, con):
    if ' rid=' not in con.data:
        note = ' '.join(con.data.split()[1:])
        theme_id = d1[id]['THEME_NOW']
        req2 = f'api/get_id_note/{note}/{theme_id}'
        note_id = get(config.address + req2).json()['answer']
        req4 = f'api/note_get_theme/{note_id}'
        theme = get(config.address + req4).json()['answer']
        if not note_id.isdigit():
            raise AttributeError("LOH")
    else:
        note_id = con.data.split('=')[-1]
        req4 = f'api/note_get_theme/{note_id}'
        theme = get(config.address + req4).json()['answer']
        req5 = f'api/note_get_header/{note_id}'
        note = get(config.address + req5).json()['answer']
    req = f'api/note_text/{note_id}'
    text = get(config.address + req).json()['answer']
    req3 = f'api/note_links/{note_id}'
    links = get(config.address + req3).json()['answer']
    s1 = {}
    s1['добавить ссылку'] = f'/add_links_to_note {theme} && {note}'
    s1['изменить текст'] = f'/set_text_to_note {theme} && {note}'
    s1['изменить название'] = f'/set_name_to_note {theme} && {note}'
    s1['удалить заметку'] = f'/del_note {theme} && {note}'
    for i in links:

        if i == 'нет ссылок' or 'нет ссылок' in i or -1 in i \
                or isinstance(i, int) or i is None or any(j is None for j in i):
            break
        s1[f'показать {i[0]}'] = f'/show_note rid={i[1]}'
    markup = create_inline_keybord(2, **s1)
    return f"""
    название - {note} \n
    тема - {theme} \n
    текст - {text} \n
    ссылки - {[i[0] for i in links]}
    """, markup


def set_name_to_note(id, con):
    message = con.data.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    note = note[2:]
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{id}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    d1[id]['name'] = note_id
    return 'напишите новое название'


def del_note(id, con):
    message = con.data.split()[1:]
    theme, note = '', ''
    k = False
    for i in message:
        if i == '&&':
            k = True
        if not k:
            theme += i
        else:
            note += i
    note = note[2:]
    req = 'api/id_from_header/'
    theme_id = str(get(config.address + req + f'/{id}/{theme}').json()['answer'])
    if not theme_id.isdigit():
        raise AttributeError("LOH")
    req2 = f'api/get_id_note/{note}/{theme_id}'
    note_id = get(config.address + req2).json()['answer']
    req = 'api/del_note'
    post(config.address + req, json={'id': note_id})
    return f'заметка {note} удалена'


def callbackupdate(update: Update, context: CallbackContext):
    id = update.effective_user.id
    add_d1(id)
    con = update.callback_query
    data = con.data
    con.answer()
    if data.startswith('/rename_theme'):
        d1[id]['changed'] = ' '.join(data.split()[1:])
        con.message.reply_text('новон название')
    elif data.startswith('/get_note_from_theme'):
        res, markup = get_notes(id, con)
        con.message.reply_text(res, reply_markup=markup)
    elif data.startswith('/show_note'):
        res, markup = show_note(id, con)
        con.message.reply_text(res, reply_markup=markup)
    elif data.startswith('/del_note'):
        res = del_note(id, con)
        con.message.reply_text(res)
    elif data.startswith('/set_name_to_note'):
        res = set_name_to_note(id, con)
        con.message.reply_text(res)
    elif data.startswith('/set_text_to_note') or data.startswith('/add_text_to_note'):
        res = add_text_to_note(id, con)
        con.message.reply_text(res)
    elif data.startswith('/add_links_to_note'):
        res = add_links_to_note(id, con)
        con.message.reply_text(res)
    elif data.startswith('/add_theme'):
        d1[id]['add_theme_name'] = True
        con.message.reply_text('напишите название новой темы')
    elif data.startswith('/add_note_to_theme'):
        d1[id]['add_note_theme'] = ' '.join(data.split()[1:])
        con.message.reply_text('напишите название новой заметки')
    elif data.startswith('/get_all_themes'):
        text, markup = get_themes(id, con)
        con.message.reply_text(text, reply_markup=markup)
    elif data.startswith('/set_user_name'):
        d1[id]['set_name'] = True
        con.message.reply_text('напишите новое имя')
    elif data.startswith('/del_theme'):
        res = del_theme(id, con)
        con.message.reply_text(res)


def main():
    updater = Updater(config.TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.contact, take_nomer))
    dispatcher.add_handler(CommandHandler("start", bot_started))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('h', help))
    dispatcher.add_handler(CallbackQueryHandler(callback=callbackupdate))
    dispatcher.add_handler(MessageHandler(Filters.text, any_text))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
