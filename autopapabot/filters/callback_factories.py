from aiogram.filters.callback_data import CallbackData


class CarMakeCallbackFactory(CallbackData, prefix="send_car_make"):
    car_make: str

