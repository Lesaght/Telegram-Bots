from aiogram.fsm.state import State, StatesGroup


class SteamForm(StatesGroup):
    waiting_profile = State()
    waiting_friends = State()
    waiting_recent = State()


class CompareForm(StatesGroup):
    waiting_first = State()
    waiting_second = State()


class LeaderboardForm(StatesGroup):
    waiting_profile = State()


class PriceTrackerForm(StatesGroup):
    waiting_item = State()
    waiting_price = State()


class InventorySearchForm(StatesGroup):
    waiting_query = State()
