from aiogram.utils.markdown import hcode

import database
import messages


def get_term_data(term: str) -> str:
    with database.BotDb() as db:
        term_data = db.get_term(term)
    if term_data:
        return (f'{hcode(term_data.term_ru)} == {hcode(term_data.term_eng)}\n'
                f'added by {term_data.added_by}\n'
                f'comments: {term_data.comments}')
    else:
        return messages.term_not_in_database
