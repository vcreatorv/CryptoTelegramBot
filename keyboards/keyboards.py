from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Currency exchange prices"),
            KeyboardButton(text="Cryptocurrency info"),
        ]
    ],
    resize_keyboard=True,
    selective=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose an option from menu..."
)

currencies = [
    "USD", "EUR", "RUB",
    "CNY", "JPY", "QAR",
    "XAU", "XAG", "XPT"
]


def currency_exchange_keyboard():
    keyboard = ReplyKeyboardBuilder()
    [keyboard.button(text=fiat) for fiat in currencies]
    keyboard.button(text='Back')
    keyboard.adjust(*[3] * 3, 1)
    return keyboard.as_markup(resize_keyboard=True)


def currency_exchange_keyboard_expanded():
    keyboard = ReplyKeyboardBuilder()

    [keyboard.button(text=fiat) for fiat in currencies]
    keyboard.button(text='Change base currency')
    keyboard.button(text='Change target currency')
    keyboard.button(text='Back')
    keyboard.adjust(*[3] * 4)
    return keyboard.as_markup(resize_keyboard=True)
