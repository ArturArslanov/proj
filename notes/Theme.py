import sqlalchemy
from sqlalchemy import orm
from . import Note
from data import db_session
from data.db_session import SqlAlchemyBase


class Theme(SqlAlchemyBase):
    __tablename__ = 'theme'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    # user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    header = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    # user = orm.relation('User')      # когда будет юзер надо будет вернуть
    orm.relation("Note", back_populates='theme')

    # тема может содержать сколько угодно идей/заметок
    @classmethod
    def add_theme(cls, header):
        session = db_session.create_session()
        if session.query(Theme).filter(Theme.header == header).first():
            return None
        theme = Theme(header=header)
        session.add(theme)
        session.commit()
        session.close()

    @classmethod
    def del_theme(cls, theme_id):
        session = db_session.create_session()
        cls.add_theme('всякое')
        anything = session.query(Theme).filter(Theme.header == 'всякое').first()
        dels = session.query(Theme).filter(Theme.id == theme_id)
        session.close()
        if dels and dels.first():
            for i in dels.first().get_notes():
                session = db_session.create_session()
                i.theme = anything
                i.theme_id = anything.id
                session.merge(i)
                session.commit()
                session.close()
        session = db_session.create_session()
        session.query(Theme).filter(Theme.id == theme_id).delete(synchronize_session='evaluate')
        session.commit()
        session.close()

    def add_note(self, text='', links=[], header=''):
        session = db_session.create_session()
        note1 = session.query(Note.Note).filter(
            Note.Note.theme_id == self.id).filter(Note.Note.header == header).first()
        links = Note.Note.ides_from_names(links) if isinstance(links, list) else links
        if note1:
            note1.links = links
            note1.text = text
        else:
            new_note = Note.Note(text=text, header=header, links=links, theme=self)
            session.add(new_note)
        session.commit()
        session.close()

    def rename_theme(self, new_header):
        self.header = new_header

    # надо будет добавить юзера

    def get_notes(self):
        session = db_session.create_session()
        notes = session.query(Note.Note).filter(Note.Note.theme_id == self.id).all()
        return notes

    def communicate_level(self):
        session = db_session.create_session()
        notes = self.get_notes()
        sum_links = 0
        for note in notes:
            for link in note.get_links():
                note2 = session.query(Note.Note).filter(Note.Note.id == int(link)).first()
                if note2 and note2.theme_id != self.id:
                    sum_links += 1
        return sum_links
