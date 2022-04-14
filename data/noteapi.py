import flask
from flask import jsonify, request

from data.Theme import Theme
from data.Note import Note

blueprint = flask.Blueprint(
    'noteapi',
    __name__,
    template_folder='../template'
)


@blueprint.route('/api/note_get_theme/', methods=['POST'])
def get_theme():
    req = request.json
    id = req['id']
    note = Note.note_from_id(id)
    answer = note.get_theme()
    return jsonify({'answer': answer})


@blueprint.route('/api/note_links/<int:id>', methods=['GET'])
def get_links(id):
    note = Note.note_from_id(id)
    answer = note.get_links()
    return jsonify({'answer': answer})


@blueprint.route('/api/note_text/<int:id>', methods=['GET'])
def get_text(id):
    note = Note.note_from_id(id)
    answer = note.text
    return jsonify({'answer': answer})


@blueprint.route('/api/set_note_header/', methods=['POST', 'PUT'])
def set_note_name():
    req = request.json
    id = req['id']
    header = req['header']
    note = Note.note_from_id(id)
    note.rename_note(header)
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
    links = new_links.split()
    note = Note.note_from_id(id)
    note.add_links(links)
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
    note = Note.note_from_id(id)
    answer = note.set_text(new_text)
    return jsonify(
        {'answer': f'{answer}'
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
