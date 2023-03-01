import random

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Text, Command

import os
import dotenv

# Read Telegram Bot API token
dotenv.load_dotenv()
token_bot: str = os.getenv('token_bot')

bot: Bot = Bot(token_bot)
dp: Dispatcher = Dispatcher()

# Amount of attempts and dict for users data
attempts: int = 5
users: dict = {}


def get_random_int(a: int = 1, b: int = 100) -> int:
    return random.randint(a, b)


@dp.message(Command(commands=['start']))
async def process_start_command(message: Message):
    await message.answer("Hi! Let`s play the game 'Guess the number OK?\n\n"
                         "Send the commands /help to get the rules of the "
                         "game and available commands")
    # add new user
    if message.from_user.id not in users:
        users[message.from_user.id] = {'in_game': False,
                                       'secret_number': None,
                                       'attempts': None,
                                       'total_games': 0,
                                       'wins': 0}


@dp.message(Command(commands=['help']))
async def process_help_commands(message: Message):
    await message.answer(f'Rules of the game:\n\nI`m thinking a number from '
                         f'1 to 100 and you`re trying guess it.\n'
                         f'You have {attempts} attempts.\n\n'
                         f'Available commands:\n/help - rules of the game '
                         f'and a list of commands\n/cancel exit from '
                         f'current game\n/stat - show statistics')


@dp.message(Command(commands=['stat']))
async def process_stat_command(message: Message):
    try:
        await message.answer(f'Total games played: '
                             f'{users[message.from_user.id]["total_games"]}\n'
                             f'Games won: {users[message.from_user.id]["wins"]}')

    except KeyError:
        await message.answer(f'Please send /start for play the game')


@dp.message(Command(commands=['cancel']))
async def process_cancel_command(message: Message):
    try:
        if users[message.from_user.id]['in_game']:
            await message.answer('You are out of the game.')
            users[message.from_user.id]['in_game'] = False
        else:
            await message.answer('You are not in the game. Let`s play!')
    except KeyError:
        await message.answer(f'Please send /start for play the game')


@dp.message(Text(text=['yes', 'ok', 'go', 'game', 'play', 'Да', 'Давай',
                       'Сыграем', 'Игра', 'Играть', 'Хочу играть'],
                 ignore_case=True))
async def process_start_game(message: Message):
    try:
        if not users[message.from_user.id]['in_game']:
            await message.answer('Nice!\nI guessed the number from 1 to 100 '
                                 'and you try to guess it.')
            users[message.from_user.id]['in_game'] = True
            users[message.from_user.id]['secret_number'] = get_random_int()
            users[message.from_user.id]['attempts'] = attempts
        else:
            await message.answer('You are in the game. Send me please '
                                 'a number from 1 to 100 or commands '
                                 '/cancel or /stat')
    except KeyError:
        await message.answer(f'Please send /start for play the game')


@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100)
async def process_game(message: Message):
    try:
        if users[message.from_user.id]['in_game']:
            if int(message.text) == users[message.from_user.id]['secret_number']:
                await message.answer('Great!!! You have guessed the number!\n\nPlay again?')
                users[message.from_user.id]['in_game'] = False
                users[message.from_user.id]['total_games'] += 1
                users[message.from_user.id]['wins'] += 1
            elif int(message.text) < users[message.from_user.id]['secret_number']:
                await message.answer('My number is greater')
                users[message.from_user.id]['attempts'] -= 1
            elif int(message.text) > users[message.from_user.id]['secret_number']:
                await message.answer('My number is lesser')
                users[message.from_user.id]['attempts'] -= 1

            if users[message.from_user.id]['attempts'] == 0:
                await message.answer(f'Unfortunately, you have no more attempts.'
                                     f'You lose :(\n\nMy number was '
                                     f'{users[message.from_user.id]["secret_number"]}'
                                     f'\n\nPlay again?')
                users[message.from_user.id]['in_game'] = False
                users[message.from_user.id]['total_games'] += 1
        else:
            await message.answer('We are not play yet(\nLet`s play?')
    except KeyError:
        await message.answer(f'Please send /start for play the game')


@dp.message()
async def process_other_answers(message: Message):
    try:
        if users[message.from_user.id]['in_game']:
            await message.answer('We`re playing now. Send me a number from 1 to 100.')
        else:
            await message.answer('I`m simple Bot. Let`s just play the game?')
    except KeyError:
        await message.answer(f'Please send /start for play the game')


if __name__ == '__main__':
    dp.run_polling(bot)
