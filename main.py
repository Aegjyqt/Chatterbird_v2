from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from dotenv import load_dotenv
import os

import database
import handler_functions
import messages

load_dotenv()
bot = Bot(
    token=os.getenv('BOT_TOKEN'),
    parse_mode='HTML'
)

dp = Dispatcher(bot=bot, storage=MemoryStorage())


class AddTermPipeline(StatesGroup):
    add_term_ru = State()
    add_term_en = State()
    add_term_comment = State()


def admin(handler: callable):
    async def wrapper(message: types.Message):
        with database.BotDb() as db:
            for user in db.get_admins():
                if message.from_user.id == user.user_id:
                    return await handler(message)
                else:
                    await message.answer('you\'re no admin!')
    return wrapper


@dp.message_handler(commands='start')
async def welcome_and_register(message: types.Message):
    with database.BotDb() as db:
        db.add_user(user_id=message.from_user.id, user_name=message.from_user.first_name)
    await message.answer(text=messages.welcome_and_register)


@dp.message_handler(commands='about')
async def about(message: types.Message):
    await message.answer(text=messages.about)


@dp.message_handler(commands='cancel', state='*')
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(f'{state} pipeline stopped')
    await state.finish()


@dp.message_handler(commands='add_term')
@admin
async def init_add_term_pipeline(message: types.Message):
    await message.answer(text='starting add_term pipeline!')
    await message.answer(text='Enter the term in Russian:')
    await AddTermPipeline.add_term_ru.set()


@dp.message_handler(state=AddTermPipeline.add_term_ru)
async def add_term_ru(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['term_ru'] = message.text
    await message.answer(text='Enter the term in English:')
    await state.set_state(AddTermPipeline.add_term_en)


@dp.message_handler(state=AddTermPipeline.add_term_en)
async def add_term_en(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['term_en'] = message.text
    await message.answer(text='Enter your comments:')
    await state.set_state(AddTermPipeline.add_term_comment)


@dp.message_handler(state=AddTermPipeline.add_term_comment)
async def add_comments(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comments'] = message.text
        data['user_id'] = message.from_user.id
        with database.BotDb() as db:
            db.add_term(term_ru=data['term_ru'], term_en=data['term_en'],
                        added_by=data['user_id'], comments=data['comments'])

    await message.answer(text='add_term pipeline finished!')
    await state.finish()


@dp.message_handler()
async def translate(message: types.Message):
    await message.answer(text=handler_functions.get_term_data(message.text))


if __name__ == "__main__":
    executor.start_polling(dp)
