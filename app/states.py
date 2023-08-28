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
    WaitingForQuantityAndPrice = State()
    WaitingForPrice = State()


class AddItem(StatesGroup):
    WaitingForPhoto = State()
    WaitingForLocation = State()
    WaitingForCity = State()
    WaitingForQuantity = State()
    WaitingForGenre = State()
    WaitingForSubgenre = State()


class ViewItem(StatesGroup):
    WaitingForCity = State()
    WaitingForGenre = State()
    WaitingForSubgenre = State()
    WaitingForQuantity = State()
    WaitingForItem = State()
