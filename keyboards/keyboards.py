import os

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

popular_currencies = [
    "USD", "EUR", "RUB",
    "CNY", "JPY", "QAR",
    "XAU", "XAG", "XPT"
]

currency_info_array = [
    [
        InlineKeyboardButton(text="Chart"),
        InlineKeyboardButton(text="News"),
    ],
    [
        InlineKeyboardButton(text="Markets"),
        InlineKeyboardButton(text="Analytics"),
    ]
]

currency_info_keyboard = InlineKeyboardMarkup(
    inline_keyboard=currency_info_array
)

currency_info_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Change cryptocurrency"),
            KeyboardButton(text="Back"),
        ]
    ],
    resize_keyboard=True,
    selective=True,
    one_time_keyboard=True,
    input_field_placeholder="Choose an option from menu..."
)


def get_currencies():
    array_of_currencies = []
    os.chdir(r"C:\Users\valer\OneDrive\Рабочий стол\3 семестр\ПиКЯП\CryptoTelegramBot\keyboards")
    with open("currencies.txt", mode='r') as file:
        lines = file.readlines()
        for line in lines:
            currency = line.split(' ')[0]
            array_of_currencies.append(currency)
    return array_of_currencies




def currency_exchange_keyboard():
    keyboard = ReplyKeyboardBuilder()
    [keyboard.button(text=fiat) for fiat in popular_currencies]
    keyboard.button(text='Back')
    keyboard.adjust(*[3] * 3, 1)
    return keyboard.as_markup(resize_keyboard=True)


def currency_exchange_keyboard_expanded():
    keyboard = ReplyKeyboardBuilder()

    [keyboard.button(text=fiat) for fiat in popular_currencies]
    keyboard.button(text='Change base currency')
    keyboard.button(text='Change target currency')
    keyboard.button(text='Back')
    keyboard.adjust(*[3] * 4)
    return keyboard.as_markup(resize_keyboard=True)


all_currencies = get_currencies()
#print('MXN'.lower() in all_currencies)