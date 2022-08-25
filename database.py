import sqlite3
from dataclasses import dataclass
import typing


@dataclass
class User:
    user_id: int = None
    user_name: str = None
    is_admin: bool = None


@dataclass
class Term:
    term_id: int = None
    term_ru: str = None
    term_eng: str = None
    added_by: int = None
    comments: str = None


class BotDb:

    def __init__(self) -> None:
        self._db = sqlite3.connect('bot.db')

    def __enter__(self):
        self.create_user_database_if_none()
        self.create_term_database_if_none()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._db.close()

    def create_user_database_if_none(self) -> None:
        cursor = self._db.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tbl_users(id INTEGER PRIMARY KEY, user_name TEXT, is_admin BOOLEAN)
                       ''')
        self._db.commit()
        cursor.close()

    def create_term_database_if_none(self) -> None:
        cursor = self._db.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tbl_terms(id INTEGER PRIMARY KEY AUTOINCREMENT, term_ru TEXT, 
                       term_en TEXT, added_by INTEGER, comments TEXT)
                       ''')
        self._db.commit()
        cursor.close()

    def create_database_log_if_none(self) -> None:
        cursor = self._db.cursor()
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tbl_log(id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT,
                       user_type TEXT, user_id INTEGER, user_name TEXT, operation TEXT, target TEXT)
                       ''')
        self._db.commit()
        cursor.close()

    def add_user(self, user_id: int, user_name: str, is_admin: bool = False) -> None:
        cursor = self._db.cursor()
        cursor.execute('''
                       INSERT OR IGNORE INTO tbl_users(id, user_name, is_admin)
                       VALUES(?,?,?)
                       ''', (user_id, user_name, is_admin))
        self._db.commit()
        cursor.close()

    def appoint_admin(self, user_id: int) -> None:
        cursor = self._db.cursor()
        cursor.execute('''
                       REPLACE INTO tbl_users(id, is_admin)
                       VALUES(?,?)
                       ''', (user_id, True))
        self._db.commit()
        cursor.close()

    def get_admins(self) -> list:
        cursor = self._db.cursor()
        cursor.execute('''
                       SELECT id, user_name, is_admin FROM tbl_users WHERE is_admin = 1
                       ''')
        all_rows = cursor.fetchall()
        admins_list = []
        for row in all_rows:
            admins_list.append(User(user_id=row[0], user_name=row[1], is_admin=row[2]))
        cursor.close()
        return admins_list

    def add_term(self, term_ru: str, term_en: str, added_by: int, comments: str):
        cursor = self._db.cursor()
        cursor.execute('''
                       INSERT OR IGNORE INTO tbl_terms(term_ru, term_en,
                       added_by, comments)
                       VALUES(?,?,?,?)
                       ''', (term_ru, term_en, added_by, comments))
        self._db.commit()
        cursor.close()

    def get_term(self, term: str) -> typing.Union[Term, None]:  # пора смотреть typing и делать сложные type hints
        cursor = self._db.cursor()
        cursor.execute('''
                       SELECT id, term_ru, term_en, added_by, comments FROM tbl_terms
                       ''')
        all_rows = cursor.fetchall()  # а вот здесь хорошо бы реализовать генератор, а не перебирать
        for row in all_rows:
            if term in row:
                return Term(term_id=row[0], term_ru=row[1], term_eng=row[2], added_by=row[3], comments=row[4])
            else:
                pass

    def log_action(self):
        """ Думаю стоит передавать в нее минимум (user_id, имя функции/переменные и время), а подробности для удобства
         пользования (is_admin, etc) распаковывать в отдельной функции """
        pass

# TODO: добавить таблицу для логов (лог важных событий и полный лог, м.б. сбор статистики) и реализовать
#  соответствующие функции + dataclass LogEntry
