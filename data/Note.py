import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase
from data import db_session


class Note(SqlAlchemyBase, SerializerMixin):
    # в заметке должны быть короткие идеи,мысли,ссылки на другие заметки или темы
    __tablename__ = 'note'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    theme_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("theme.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    links = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    header = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    theme = orm.relation('Theme')

    @classmethod
    def del_note(cls, note_id):
        session = db_session.create_session()
        session.query(Note).filter(Note.id == note_id).delete(synchronize_session='evaluate')
        session.commit()
        session.close()

    def rename_note(self, header):
        self.header = header

    def get_links(self):
        return self.links.split()

    def get_theme(self):
        return self.theme

    @classmethod
    def note_from_id(cls, id):
        session = db_session.create_session()
        note = session.query(Note).filter(Note.id == id).first()
        session.close()
        return note

    def add_links(self, new_links: list):
        self.links = self.links + ' ' + ' '.join(new_links)

    def set_links(self, new_links):
        if isinstance(new_links, list):
            self.links = ' '.join(new_links)
            return 'successfully set links'
        if isinstance(new_links, str):
            self.links = new_links
            return 'successfully set links'

        return f'TYPE ERROR: cannot set links it must be (list(str) or str)'

    def deleted_links(self, links: list):
        old_links = self.links
        new_links = []
        for i in old_links:
            if i not in links:
                new_links.append([i])
        return self.set_links(new_links)

    def set_text(self, new_text):
        self.text = new_text
        return f'successfully set text'

