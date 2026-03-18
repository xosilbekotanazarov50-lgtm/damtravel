from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    name = State()
    phone = State()
    destination = State()
    people_count = State()
    time = State()


class AdminCallState(StatesGroup):
    confirming = State()
