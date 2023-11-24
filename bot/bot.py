import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from configs.config import configuration
from keyboards import keyboards
from FSM.StateMachine import ExchangeCurrency
from FSM.StateMachine import Menu
from api.api import api_crypto

logging.basicConfig(filename="../static/logger.txt", level=logging.INFO)
dp = Dispatcher()
bot = Bot(token=configuration.BOT_TOKEN.get_secret_value(), parse_mode="html")


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Hello, Aiogram 3.x!", reply_markup=keyboards.main_keyboard)
    await message.answer('Choose an option')
    await state.set_state(Menu.option)


@dp.message(Menu.option, F.text.in_(Menu.menu))
async def menu_option(message: types.Message, state: FSMContext):
    await state.update_data(option=message.text)
    await message.answer("Choose a <i>base currency</i> from the following list :)",
                         reply_markup=keyboards.currency_exchange_keyboard())
    await state.set_state(ExchangeCurrency.base_currency)

# @dp.message(F.text.lower() == "currency exchange prices")
# async def exchange_base_currency(message: types.Message, state: FSMContext):
#     await message.answer("Choose a <i>base currency</i> from the following list :)",
#                          reply_markup=keyboards.currency_exchange_keyboard())
#     # await state.set_state(ExchangeCurrency.base_currency)


@dp.message(ExchangeCurrency.base_currency, F.text.in_(keyboards.currencies))
async def exchange_target_currency(message: types.Message, state: FSMContext):
    await state.update_data(chosen_base_currency=message.text.upper())
    exchange = await state.get_data()
    await message.reply(f"You've chosen <b>{exchange['chosen_base_currency']}</b> as base currency. "
                        f"Now choose a <i>target currency</i> from the list below :)",
                        reply_markup=keyboards.currency_exchange_keyboard())
    await state.set_state(ExchangeCurrency.target_currency)


@dp.message(ExchangeCurrency.target_currency, F.text.in_(keyboards.currencies))
async def exchange_procedure(message: types.Message, state: FSMContext):
    await state.update_data(chosen_target_currency=message.text.upper())
    exchange = await state.get_data()
    base_currency = exchange['chosen_base_currency']
    target_currency = exchange['chosen_target_currency']
    await message.reply(
        f"You've chosen <b>{base_currency}</b> as base currency"
        f" and <b>{target_currency}</b> as target currency.")
    await message.answer(text='Please set the currency amount for converting')
    await state.set_state(ExchangeCurrency.amount)

    # parameters = {
    #     "amount": 100,
    #     "symbol": base_currency,
    #     "convert": target_currency
    # }
    # response = api_crypto(parameters)
    # conversion = response["data"][0]["quote"][target_currency]["price"]
    # await message.answer(f"100 <b>{base_currency}</b> equals {conversion} <b>{target_currency}</b>")


@dp.message(ExchangeCurrency.amount)
async def currency_amount(message: types.Message, state: FSMContext):
    await state.update_data(amount=message.text)
    exchange = await state.get_data()
    amount_for_converse = exchange['amount']
    if message.text.isdigit():
        base_currency = exchange['chosen_base_currency']
        target_currency = exchange['chosen_target_currency']
        await message.answer(f'You are going to converse {amount_for_converse} units of {base_currency} into'
                             f' {target_currency}')
        parameters = {
            "amount": int(amount_for_converse),
            "symbol": base_currency,
            "convert": target_currency
        }
        response = api_crypto(parameters)
        conversion = response["data"][0]["quote"][target_currency]["price"]
        await message.answer(
            f"{amount_for_converse} <b>{base_currency}</b> equals {conversion} <b>{target_currency}</b>",
            reply_markup=keyboards.currency_exchange_keyboard_expanded())
        await state.clear()

    else:
        await message.answer('Wrong data. Please try again')
        return await state.set_state(ExchangeCurrency.amount)


@dp.message(F.text.lower().in_(['back']))
async def back(message: types.Message, state: FSMContext):
    print(6)
    await state.clear()
    await state.set_state(Menu.option)
    return await message.answer(text = 'back',reply_markup=keyboards.main_keyboard)


@dp.message()
async def wrong_input(message: types.Message):
    await message.answer('Wrong data')


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
