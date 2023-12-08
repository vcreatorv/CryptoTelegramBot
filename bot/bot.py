import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from configs.config import configuration
from keyboards import keyboards
from FSM.StateMachine import ExchangeCurrency, InfoCurrency
from FSM.StateMachine import Menu
from api.api import api_crypto_exchange, api_crypto_info

logging.basicConfig(filename="../static/logger.txt", level=logging.INFO)
dp = Dispatcher()
bot = Bot(token=configuration.BOT_TOKEN.get_secret_value(), parse_mode="html")


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(f"Hello, {message.from_user.username}! Choose an option!",
                         reply_markup=keyboards.main_keyboard)
    await state.set_state(Menu.option)


@dp.message(F.text.lower().in_(['back']))
async def back(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.clear()
    if change_flag[0]:
        change_flag[0] = False
    await state.set_state(Menu.option)
    return await message.answer(text='back', reply_markup=keyboards.main_keyboard)


@dp.message(Menu.option, F.text.in_(Menu.menu))
async def menu_option(message: types.Message, state: FSMContext):
    await state.update_data(option=message.text)
    # await message.answer("Choose a <i>base currency</i> from the following list :)",
    #                      reply_markup=keyboards.currency_exchange_keyboard())
    if message.text.lower() == "currency exchange prices":
        await message.answer("Choose a <i>base currency</i> from the following list :)",
                             reply_markup=keyboards.currency_exchange_keyboard())
        await state.set_state(ExchangeCurrency.base_currency)
    elif message.text.lower() == "cryptocurrency info":
        await message.answer("Set the cryptocurrency")
        await state.set_state(InfoCurrency.info_currency)


@dp.message(ExchangeCurrency.base_currency, F.text.in_(keyboards.currencies))
async def exchange_target_currency(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.update_data(chosen_base_currency=message.text.upper())
    exchange = await state.get_data()
    if not change_flag[0]:
        await message.reply(f"You've chosen <b>{exchange['chosen_base_currency']}</b> as base currency. "
                            f"Now choose a <i>target currency</i> from the list below :)",
                            reply_markup=keyboards.currency_exchange_keyboard())
        await state.set_state(ExchangeCurrency.target_currency)
    else:
        await message.reply('Set the currency amount for converting')
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
    await message.answer(text='Please set the currency amount for converting')
    await state.set_state(ExchangeCurrency.amount)


@dp.message(ExchangeCurrency.amount)
async def currency_amount(message: types.Message, state: FSMContext, change_flag: list[bool]):
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
        response = api_crypto_exchange(parameters)
        conversion = response["data"][0]["quote"][target_currency]["price"]
        await message.answer(
            f"{amount_for_converse} <b>{base_currency}</b> equals {conversion} <b>{target_currency}</b>",
            reply_markup=keyboards.currency_exchange_keyboard_expanded())
        change_flag[0] = False
        return await state.set_state(ExchangeCurrency.next_step)

    else:
        change_flag[0] = False
        await message.answer('Wrong data. Please try again')
        return await state.set_state(ExchangeCurrency.amount)


@dp.message(ExchangeCurrency.next_step)
async def next_step(message: types.Message, state: FSMContext, change_flag: list[bool]):
    await state.update_data(step=message.text)
    if message.text.lower() == "change base currency":
        change_flag[0] = True
        await state.set_state(ExchangeCurrency.base_currency)
        return await message.answer(text='Choose a new base currency',
                                    reply_markup=keyboards.currency_exchange_keyboard())
    if message.text.lower() == 'change target currency':
        change_flag[0] = True
        await state.set_state(ExchangeCurrency.target_currency)
        return await message.answer(text='Choose a new target currency',
                                    reply_markup=keyboards.currency_exchange_keyboard())


@dp.message(InfoCurrency.info_currency)
async def info_currency(message: types.Message, state: FSMContext):
    await state.update_data(set_currency=message.text)
    info = await state.get_data()
    currency = info["set_currency"].upper()
    response = api_crypto_info(currency)
    print(response)
    keyboards.currency_info_array[0][0].url = f"https://coinmarketcap.com/currencies/{response['Name'].lower()}/#Chart"
    keyboards.currency_info_array[0][1].url = f"https://coinmarketcap.com/currencies/{response['Name'].lower()}/#News"
    keyboards.currency_info_array[1][0].url = f"https://coinmarketcap.com/currencies/{response['Name'].lower()}/#Markets"
    keyboards.currency_info_array[1][1].url = f"https://coinmarketcap.com/currencies/{response['Name'].lower()}/#Analytics"
    await message.reply(text=f"Name: {response['Name']}\n"
                              f"Price: {response['Price']}\n"
                              f"1hr Change: {response['1hr Change']}\n"
                              f"24hr Change: {response['24hr Change']}\n"
                              f"7d Change: {response['7d Change']}\n"
                              f"Volume: {response['Volume']}\n"
                              f"Market Cap: {response['Market Cap']}\n"
                              f"Circulating Supply: {response['Circulating Supply']}\n"
                              f"Total Supply: {response['Total Supply']}",
                         reply_markup=keyboards.currency_info_keyboard)
    await state.set_state(Menu.option)
    # await message.answer(reply_markup=keyboards.currency_info_menu)

@dp.message()
async def wrong_input(message: types.Message):
    await message.answer('Wrong data')


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, change_flag=[False])


if __name__ == "__main__":
    asyncio.run(main())
