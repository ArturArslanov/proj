import flask
from flask import jsonify, request

from data import db_session
from data.Theme import Theme
from data.Note import Note
from data.User import User

blueprint = flask.Blueprint(
    'noteapi',
    __name__,
    template_folder='../template'
)


@blueprint.route('/api/note_get_theme/<int:id>', methods=['GET'])
def get_theme(id):
    session = db_session.create_session()
    note = session.query(Note).filter(Note.id == id).first()
    theme_header = note.theme.header
    session.close()
    return jsonify({'answer': theme_header})


@blueprint.route('/api/note_links/<int:id>', methods=['GET'])
def get_links(id):
    note = Note.note_from_id(id)
    answer = note.get_links()
    if answer:
        return jsonify({'answer': answer})
    else:
        return jsonify({'answer': 'нет ссылок'})


@blueprint.route('/api/note_text/<int:id>', methods=['GET'])
def get_text(id):
    note = Note.note_from_id(id)
    answer = note.text
    return jsonify({'answer': answer})


@blueprint.route('/api/set_note_header/', methods=['POST', 'PUT'])
def set_note_name():
    res = request.json
    header = res['new_header']
    id = res['id']
    session = db_session.create_session()
    note = session.query(Note).filter(Note.id == id).first()
    note.header = header
    session.commit()
    session.close()
    return jsonify(
        {'answer': f'successfully set header'
         }
    )


@blueprint.route('/api/set_note_theme/', methods=['POST', 'PUT'])
def set_note_theme():
    req = request.json
    id = req['id']
    theme_id = req['theme_id']
    note = Note.note_from_id(id)
    theme = Theme.theme_from_id(theme_id)
    theme.add_note(text=note.text, links=note.links, header=note.header)
    Note.del_note(id)
    return jsonify(
        {'answer': f'successfully set theme'
         }
    )


@blueprint.route('/api/add_links/', methods=['POST', 'PUT'])
def add_links():
    req = request.json
    id = req['id']
    new_links = req['new_links']
    user_id = req['user_id']
    links = new_links.split('~')
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    real_note = session.query(Note).filter(Note.id == id).first()
    themes = user.all_themes()
    any_id = ''
    for i in themes:
        theme = session.query(Theme).filter(Theme.id == i).first()
        if theme.header == 'всякое':
            any_id = i
        notes = theme.get_notes()
        header_notes = [note.header for note in notes]
        for k in range(len(header_notes)):
            if header_notes[k] in links:
                real_note.links = real_note.links + ' ' + f'{notes[k].id}'
                del links[links.index(header_notes[k])]
    session.commit()
    session.close()
    any_theme = Theme.theme_from_id(any_id)
    for i in links:
        any_theme.add_note(text='', links='', header=f'{i}')
    session = db_session.create_session()
    user = session.query(User).filter(User.id == user_id).first()
    real_note = session.query(Note).filter(Note.id == id).first()
    themes = user.all_themes()
    for i in themes:
        theme = session.query(Theme).filter(Theme.id == i).first()
        notes = theme.get_notes()
        header_notes = [note.header for note in notes]
        for k in range(len(header_notes)):
            if header_notes[k] in links:
                real_note.links = real_note.links + ' ' + f'{notes[k].id}'
                del links[links.index(header_notes[k])]
    session.commit()
    session.close()

    return jsonify(
        {'answer': f'successfully add links'
         }
    )


@blueprint.route('/api/del_links/', methods=['POST', 'PUT', 'DELETE'])
def del_links():
    req = request.json
    id = req['id']
    links = req['links']
    note = Note.note_from_id(id)
    links = links.split()
    answer = note.deleted_links(links)
    return jsonify(
        {'answer': f'{answer}'
         }
    )


@blueprint.route('/api/set_texts/', methods=['POST', 'PUT'])
def set_text():
    req = request.json
    id = req['id']
    new_text = req['new_text']
    session = db_session.create_session()
    note = session.query(Note).filter(Note.id == id).first()
    note.text = new_text
    session.commit()
    session.close()
    return jsonify(
        {'answer': f'удачно надеюсь'
         }
    )


@blueprint.route('/api/links_to_note/<int:id>', methods=['GET'])
def links_to_note():
    note = Note.note_from_id(id)
    theme = note.get_theme()
    theme.get_notes()
    user = theme.user
    s1 = []
    for them in user.all_themes():
        for not2 in them.get_notes():
            if str(note.id) in not2.links.split():
                s1.append(not2.id)
                break
    return jsonify(
        {'answer': f'{s1}'}
    )


@blueprint.route('/api/get_id_note/<string:header>/<int:theme_id>', methods=['GET'])
def get_id_from_header(header, theme_id):
    session = db_session.create_session()
    id = session.query(Note.id).filter(Note.header == header and Note.theme_id == theme_id).first()[
        0]
    session.close()
    return jsonify(
        {'answer': f'{id}'}
    )


@blueprint.route('/api/del_note', methods=['DEL', 'POST'])
def del_note():
    req = request.json
    id = req['id']
    Note.del_note(id)
    return jsonify(
        {'answer': f'deleted'}
    )

