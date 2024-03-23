from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Message, Chat
from fluent.runtime import FluentLocalization
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from bot.config_reader import admin_chat_id
from bot.db.db import add_element_to_admin_table, delete_admin_element, check_element_in_db_by_id, get_all_admin_elements, check_element_in_db, update_admin_elements

from bot.states.elements import Elements
from bot.keyboards.user_btns import kb
from bot.keyboards.admin_btns import choice_kb, adm_kb, cancel_kb
from bot.filters.admin import AdminFilter

from logging import info


admins = list(map(int, admin_chat_id.split(',')))

router = Router()
router.message.filter(F.chat.id.in_(admins))


def extract_id(message: Message) -> str:
    """
    Извлекает ID юзера из хэштега в сообщении

    :param message: сообщение, из хэштега в котором нужно достать айди пользователя
    :return: ID пользователя, извлечённый из хэштега в сообщении
    """
    # Получение списка сущностей (entities) из текста или подписи к медиафайлу в отвечаемом сообщении
    entities = message.entities or message.caption_entities
    # Если всё сделано верно, то последняя (или единственная) сущность должна быть хэштегом...
    if not entities or entities[-1].type != "hashtag":
        raise ValueError("Не удалось извлечь ID для ответа!")

    # ... более того, хэштег должен иметь вид #id123456, где 123456 — ID получателя
    hashtag = entities[-1].extract_from(message.text or message.caption)
    if len(hashtag) < 4 or not hashtag[3:].isdigit():  # либо просто #id, либо #idНЕЦИФРЫ
        raise ValueError("Некорректный ID для ответа!")

    return str(hashtag[3:])

@router.message(F.reply_to_message)
async def reply_to_user(message: Message):
    """
    Ответ администратора на сообщение юзера (отправленное ботом).
    Используется метод copy_message, поэтому ответить можно чем угодно, хоть опросом.

    :param message: сообщение от админа, являющееся ответом на другое сообщение
    :param l10n: объект локализации
    """

    # Вырезаем ID
    try:
        user_id = extract_id(message.reply_to_message)
    except ValueError as ex:
        return await message.reply(str(ex))

    # Пробуем отправить копию сообщения.
    # В теории, это можно оформить через errors_handler, но мне так нагляднее
    await message.bot.send_message(text='Отвечаем:', chat_id=user_id, reply_markup=kb)
    await message.copy_to(user_id)

@router.message(F.text == 'Просмотреть таблицу')
async def show_admin_table(message: Message):
    table = ''
    admin_elements = await get_all_admin_elements()
    # Сортируем список элементов по возрастанию element_id
    sorted_admin_elements = sorted(admin_elements, key=lambda element: element.element_id)
    for element in sorted_admin_elements:
        new_line = f"{element.element_id} {element.name}\n"
        # Проверяем, превысит ли добавление новой строки предел
        if len(table) + len(new_line) > 3500:
            # Если да, отправляем текущее содержимое table и очищаем ее
            await message.answer(table, parse_mode="HTML")        
            table = ''
        # Добавляем данные в таблицу
        table += new_line
    
    # После выхода из цикла проверяем, есть ли оставшиеся данные в table
    if table:
        # Если да, отправляем оставшееся содержимое table
        await message.answer(table, parse_mode="HTML")


@router.message(F.text == 'Отмена')
async def usr_to_adm_1(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admins:
        await message.answer('Действие отменено', reply_markup=adm_kb)
    else:
        await message.answer('Действие отменено', reply_markup=kb)

@router.message(StateFilter(None), F.text == 'Добавить элемент(ы) в таблицу')
async def add_element(message: Message, state: FSMContext):
    await state.set_state(Elements.add_element_id)
    await message.answer('Введите элемент(ы):', reply_markup=cancel_kb)

@router.message(StateFilter(Elements.add_element_id), F.text)
async def add_element_id(message: Message, state: FSMContext):
    msg = message.text.split('\n')
    elements = []
    for i in msg:
        elements += [i.split(' ')]
    new_elements = [(int(el[0]), " ".join(el[1:])) for el in elements]
    await update_admin_elements(new_elements)
    await message.answer('Элементы успешно добавлены', reply_markup=adm_kb)
    await state.clear()

    # x = await check_element_in_db_by_id(int(message.text))
    # if not x:
    #     await state.update_data(id_=message.text)
    #     await state.set_state(Elements.add_element_name)
    #     await message.answer('Введите название элемента:')
    # else:
    #     await message.answer('Элемент с таким айди уже существует! Напишите другой айди.', reply_markup=cancel_kb)

# @router.message(StateFilter(Elements.add_element_name), F.text)
# async def add_element_name(message: Message, state: FSMContext):
#     await state.update_data(element_name=message.text)
#     await state.set_state(Elements.add_element_desc)
#     await message.answer('Вы будете вводить описание элемента?', reply_markup=choice_kb)

# @router.message(StateFilter(Elements.add_element_desc), F.text == 'Буду')
# async def add_element_desc(message: Message, state: FSMContext):
#     await message.answer('Введите описание элемента:')
#     await state.set_state(Elements.add_element_desc_2)

# @router.message(StateFilter(Elements.add_element_desc_2), F.text)
# async def add_element_desc_2(message: Message, state: FSMContext):
#     await state.update_data(comment=message.text)
#     #Здесь нужно вытащить дату и запихать ее в функцию
#     data = await state.get_data()
#     await add_element_to_admin_table(int(data["id_"]), data["element_name"], data["comment"])
#     info (data)
#     await message.answer('Элемент успешно добавлен!', reply_markup=adm_kb)
#     #Также наверное нужно очистить дату, я не нашел как
#     await state.set_data({})
#     await state.clear()

# @router.message(StateFilter(Elements.add_element_desc), F.text == 'Не буду')
# async def add_element_desc(message: Message, state: FSMContext):
#     #Здесь нужно вытащить дату и запихать ее в функцию
#     data = await state.get_data()
#     await add_element_to_admin_table(int(data["id_"]), data["element_name"], '')
#     await message.answer('Элемент успешно добавлен!', reply_markup=adm_kb)
#     #Также наверное нужно очистить дату, я не нашел как
#     await state.set_data({})
#     await state.clear()

@router.message(F.text == 'Удалить элемент')
async def remove_element(message: Message, state: FSMContext):
    #Тут тоже хз как это сделать, нужно как-то спрашивать какой элемент удалить, потом находить в базе этот элемент и удалять, как это сделать я не знаю
    await message.answer('Введите номер элемента для удаления:', reply_markup=cancel_kb)
    await state.set_state(Elements.remove_element_by_id)

@router.message(StateFilter(Elements.remove_element_by_id))
async def add_element_desc(message: Message, state: FSMContext):
    try:
        x = await delete_admin_element(int(message.text))
    except ValueError: 
        await message.answer('Введите число')
        return
    
    if x:
        await message.answer('Элемент успешно удален!', reply_markup=adm_kb)
    else:
        await message.answer('Такого элемента не существует', reply_markup=cancel_kb)    
        return
    await state.set_state(default_state)
