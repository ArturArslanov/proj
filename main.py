from data import db_session
from config import bd_path
from notes.Note import Note
from notes.Theme import Theme


def main():
    db_session.global_init(bd_path)
    session = db_session.create_session()
    theme2 = session.query(Theme).filter(Theme.header == 'искусство').first()
    theme2.rename_theme('психология')
    session.close()


if __name__ == "__main__":
    main()
