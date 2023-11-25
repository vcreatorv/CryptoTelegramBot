from aiogram.fsm.state import StatesGroup, State


class ExchangeCurrency(StatesGroup):
    base_currency: str = State()
    target_currency: str = State()
    amount: str = State()
    next_step : str = State()


class Menu(StatesGroup):
    option: str = State()
    menu = ["Currency exchange prices", "Cryptocurrency info"]
