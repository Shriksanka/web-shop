from aiogram.dispatcher.filters.state import StatesGroup, State


class AddCity(StatesGroup):
    WaitingForCity = State()


class AddQuantity(StatesGroup):
    WaitingForQuantity = State()


class AddGenre(StatesGroup):
    WaitingForGenre = State()


class AddSubgenre(StatesGroup):
    WaitingForSubgenreName = State()
    WaitingForSubgenreDescription = State()
    WaitingForSubgenrePhoto = State()
    WaitingForGenreChoice = State()
