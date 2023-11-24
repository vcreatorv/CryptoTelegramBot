import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from configs.config import configuration
from keyboards import keyboards
from FSM.StateMachine import ExchangeCurrency
from api.api import api_crypto

logging.basicConfig(filename="../static/logger.txt", level=logging.INFO)
dp = Dispatcher()
bot = Bot(token=configuration.BOT_TOKEN.get_secret_value(), parse_mode="html")


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, Aiogram 3.x!", reply_markup=keyboards.main_keyboard)


@dp.message(F.text.lower() == "currency exchange prices")
async def exchange_base_currency(message: types.Message, state: FSMContext):
    await message.answer("Choose a <i>base currency</i> from the following list :)",
                         reply_markup=keyboards.currency_exchange_keyboard())
    await state.set_state(ExchangeCurrency.base_currency)


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

    parameters = {
        "amount": 100,
        "symbol": base_currency,
        "convert": target_currency
    }
    response = api_crypto(parameters)
    conversion = response["data"][0]["quote"][target_currency]["price"]
    await message.answer(f"100 <b>{base_currency}</b> equals {conversion} <b>{target_currency}</b>")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
