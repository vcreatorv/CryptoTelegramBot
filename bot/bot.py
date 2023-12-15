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
    await message.answer(f"Hello, {message.from_user.username}! Welcome to NIVACryptoBot 📈\n\n"
                         f"Choose an option on your keyboard 📲",
                         reply_markup=keyboards.main_keyboard)
    await state.set_state(Menu.option)


@dp.message(F.text.lower().in_(['back']))
async def back(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.clear()
    if change_flag[0]:
        change_flag[0] = False
    await state.set_state(Menu.option)
    return await message.answer(text='Back to Menu', reply_markup=keyboards.main_keyboard)


@dp.message(Menu.option, F.text.in_("Currency exchange prices"))
async def menu_option(message: types.Message, state: FSMContext):
    await state.update_data(option=message.text)
    await message.answer("Choose a <i>base currency</i> on your keyboard 💱",
                         reply_markup=keyboards.currency_exchange_keyboard())
    await state.set_state(ExchangeCurrency.base_currency)


@dp.message(ExchangeCurrency.base_currency, F.text.in_(keyboards.currencies))
async def exchange_target_currency(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.update_data(chosen_base_currency=message.text.upper())
    exchange = await state.get_data()
    if not change_flag[0]:
        await message.reply(f"You've chosen <b>{exchange['chosen_base_currency']}</b> as base currency. "
                            f"Now choose a <i>target currency</i> on your keyboard 💱",
                            reply_markup=keyboards.currency_exchange_keyboard())
        await state.set_state(ExchangeCurrency.target_currency)
    else:
        await message.reply("Please, set the currency amount for converting ⬇️")
        await state.set_state(ExchangeCurrency.amount)


@dp.message(ExchangeCurrency.target_currency, F.text.in_(keyboards.currencies))
async def exchange_procedure(message: types.Message, state: FSMContext):
    await state.update_data(chosen_target_currency=message.text.upper())
    exchange = await state.get_data()
    base_currency = exchange['chosen_base_currency']
    target_currency = exchange['chosen_target_currency']
    await message.reply(
        f"You've chosen <b>{base_currency}</b> as base currency"
        f" and <b>{target_currency}</b> as target currency.")
    await message.answer(text='Please, set the currency amount for converting ⬇️')
    await state.set_state(ExchangeCurrency.amount)


@dp.message(ExchangeCurrency.amount)
async def currency_amount(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.update_data(amount=message.text)
    exchange = await state.get_data()
    amount_for_converse = exchange['amount']
    if message.text.isdigit():
        base_currency = exchange['chosen_base_currency']
        target_currency = exchange['chosen_target_currency']

        parameters = {
            "amount": int(amount_for_converse),
            "symbol": base_currency,
            "convert": target_currency
        }

        response = api_crypto(parameters)
        conversion = response["data"][0]["quote"][target_currency]["price"]
        await message.answer(
            f'You are going to converse <b>{float(amount_for_converse):,}</b> units of <b>{base_currency}</b> into'
            f' <b>{target_currency}</b>\n\n'f"{float(amount_for_converse):,} <b>{base_currency}</b> equals {conversion:,.2f} <b>{target_currency}</b>",
            reply_markup=keyboards.currency_exchange_keyboard_expanded())
        change_flag[0] = False
        return await state.set_state(ExchangeCurrency.next_step)
    else:
        change_flag[0] = False
        await message.answer('Wrong data. Please, try again')
        return await state.set_state(ExchangeCurrency.amount)


@dp.message(ExchangeCurrency.next_step)
async def next_step(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.update_data(step=message.text)
    if message.text.lower() == "change base currency":
        change_flag[0] = True
        await state.set_state(ExchangeCurrency.base_currency)
        return await message.answer(text='Choose a new base currency on your keyboard',
                                    reply_markup=keyboards.currency_exchange_keyboard())
    if message.text.lower() == 'change target currency':
        change_flag[0] = True
        await state.set_state(ExchangeCurrency.target_currency)
        return await message.answer(text='Choose a new target currency on your keyboard',
                                    reply_markup=keyboards.currency_exchange_keyboard())


@dp.message()
async def wrong_input(message: types.Message):
    await message.answer('Wrong data. Please, try again')


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, change_flag=[False])


if __name__ == "__main__":
    asyncio.run(main())
