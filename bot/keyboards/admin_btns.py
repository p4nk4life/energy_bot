from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard_adm = [[KeyboardButton(text='Просмотреть таблицу')], [KeyboardButton(text='Добавить элемент(ы) в таблицу'), KeyboardButton(text='Удалить элемент')], [KeyboardButton(text='Коллекция ОС'), KeyboardButton(text='Задать вопрос'), KeyboardButton(text='Добавить элемент')]]
adm_kb = ReplyKeyboardMarkup(keyboard=keyboard_adm, resize_keyboard=True)

keyboard = [[KeyboardButton(text='Буду'), KeyboardButton(text='Не буду')]]
choice_kb = ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

keyboard_cancel = [[KeyboardButton(text='Отмена')]]
cancel_kb = ReplyKeyboardMarkup(keyboard=keyboard_cancel, resize_keyboard=True, input_field_placeholder='Нажмите на кнопку')