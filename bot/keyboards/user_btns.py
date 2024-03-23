from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = [[KeyboardButton(text='Коллекция ОС'), KeyboardButton(text='Добавить элемент'), KeyboardButton(text='Задать вопрос')]]
kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
