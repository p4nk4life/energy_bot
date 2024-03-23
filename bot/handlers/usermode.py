from asyncio import create_task, sleep

from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import ContentType
from aiogram.types import Message
from fluent.runtime import FluentLocalization

from bot.blocklists import banned, shadowbanned
from bot.config_reader import admin_chat_id
from bot.filters import SupportedMediaFilter
from bot.db.db import create_user, create_element, add_element_to_user, get_user_by_telegram_id, \
    get_elements_by_user_telegram_id, check_element_in_db, check_user, get_all_admin_elements, remove_user_elements
from bot.db.models import User, Element, UserElementLink
from bot.keyboards.user_btns import kb
from bot.keyboards.admin_btns import adm_kb, cancel_kb
from aiogram import F
from logging import info, debug

from aiogram.fsm.context import FSMContext
from bot.states.dialog import Dialog_admin
from bot.states.elements import Elements

from bot.handlers.adminmode import admins


router = Router()


async def _send_expiring_notification(message: Message, l10n: FluentLocalization):
    """
    Отправляет "самоуничтожающееся" через 5 секунд сообщение

    :param message: сообщение, на которое бот отвечает подтверждением отправки
    :param l10n: объект локализации
    """
    msg = await message.reply(l10n.format_value("sent-confirmation"))

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    debug(message.from_user.id)
    debug(f"adm_chat_id: {admin_chat_id}")
    debug(f"list_admins: {admins}")
    info(await check_user(str(message.from_user.id)))
    
    if message.from_user.username and not await check_user(str(message.from_user.id)):
        user = await create_user(message.from_user.username, '', str(message.from_user.id))
    elif not await check_user(str(message.from_user.id)):
        user = await create_user('no_username', '', str(message.from_user.id))  
    
    if message.from_user.id in admins:
        await message.answer(
            'Добро пожаловать в чат-бот “Коллекция Открытого Сознания” для практиков Энергетических Медитаций! Здесь ты можешь коллекционировать и всегда иметь под рукой все полученные тобой Элементы Сознания.\n\nПользоваться чат-ботом очень просто. Нажми кнопку “Добавить элемент”, введи его название и твоя коллекция пополнится! Далее нажав кнопку “Коллекция ОС” ты увидишь свою коллекцию, где нумерация может идти не по порядку и соответствует Большому Списку всех Элементов Сознания. По номерам ты можешь узнать – сколько элементов еще предстоит найти и изучить. Мы рекомендуем вводить в список только те Элементы Сознания, которые ты уже практиковал хотя бы один раз. Также можно всегда задать вопрос команде “Открытого Сознания”, используя соответствующую кнопку.\n\nЧтобы начать - посмотри вводное видео про Энергетические Медитации, запусти себе первый Элемент Сознания “Белый Процесс” и заведи его в таблицу. Желаем интересного и увлекательного путешествия роста сознания!\n\nВводное видео:\nhttps://www.youtube.com/watch?v=mLFQeJaQrzI&t=810s\n\nНаши ссылки:\n➡Телеграмм канал - https://t.me/dmitdemin_os\n➡TG чат: общение, тусовка, вопросы - https://t.me/demintusa\n➡YouTube https://www.youtube.com/@dmitdemin\n➡Сайт с актуальными программами https://dmitdemin.ru/', reply_markup=adm_kb)
    else:          
        await message.answer(
            'Добро пожаловать в чат-бот “Коллекция Открытого Сознания” для практиков Энергетических Медитаций! Здесь ты можешь коллекционировать и всегда иметь под рукой все полученные тобой Элементы Сознания.\n\nПользоваться чат-ботом очень просто. Нажми кнопку “Добавить элемент”, введи его название и твоя коллекция пополнится! Далее нажав кнопку “Коллекция ОС” ты увидишь свою коллекцию, где нумерация может идти не по порядку и соответствует Большому Списку всех Элементов Сознания. По номерам ты можешь узнать – сколько элементов еще предстоит найти и изучить. Мы рекомендуем вводить в список только те Элементы Сознания, которые ты уже практиковал хотя бы один раз. Также можно всегда задать вопрос команде “Открытого Сознания”, используя соответствующую кнопку.\n\nЧтобы начать - посмотри вводное видео про Энергетические Медитации, запусти себе первый Элемент Сознания “Белый Процесс” и заведи его в таблицу. Желаем интересного и увлекательного путешествия роста сознания!\n\nВводное видео:\nhttps://www.youtube.com/watch?v=mLFQeJaQrzI&t=810s\n\nНаши ссылки:\n➡Телеграмм канал - https://t.me/dmitdemin_os\n➡TG чат: общение, тусовка, вопросы - https://t.me/demintusa\n➡YouTube https://www.youtube.com/@dmitdemin\n➡Сайт с актуальными программами https://dmitdemin.ru/', reply_markup=kb)

@router.message(F.text == "Коллекция ОС")
async def collection_OS(message: Message, bot: Bot):
    user_elements = await get_elements_by_user_telegram_id(str(message.from_user.id))
    if user_elements is None or not user_elements:
        await message.answer("Коллекция пуста")
        return

    admin_elements = await get_all_admin_elements()
    admin_element_names = {element.name for element in admin_elements}

    # Определение названий элементов пользователя, которые нужно удалить
    elements_to_remove = [element.name for element in user_elements if element.name not in admin_element_names]

    # Удаление ненужных элементов пользователя по названию
    if elements_to_remove:
        await remove_user_elements(str(message.from_user.id), elements_to_remove)

    # Формирование и отправка обновленного списка элементов пользователя
    user_elements = await get_elements_by_user_telegram_id(str(message.from_user.id))
    table = ''
    sorted_user_elements = sorted(user_elements, key=lambda element: element.element_id)
    
    for element in sorted_user_elements:
        new_line = f"{element.element_id} {element.name}\n"
        if len(table) + len(new_line) > 3500:
            await message.answer(table, parse_mode="HTML")        
            table = ''
        table += new_line
    
    if table:
        await message.answer(table, parse_mode="HTML")

@router.message(F.text == 'Отмена')
async def usr_to_adm_1(message: Message, state: FSMContext):
    await state.clear()
    if message.from_user.id in admins:
        await message.answer('Действие отменено', reply_markup=adm_kb)
    else:
        await message.answer('Действие отменено', reply_markup=kb)

@router.message(F.text == 'Задать вопрос')
async def usr_to_adm_1(message: Message, state: FSMContext):
    await state.set_state(Dialog_admin.usr_to_adm)
    await message.answer("Введите свой вопрос", reply_markup=cancel_kb)

@router.message(Dialog_admin.usr_to_adm, F.text)
async def usr_to_adm_2(message: Message, state: FSMContext):
    await message.bot.send_message(chat_id=120089808, text=f"Вам пришло новое сообщение от пользователя!\n\n{message.text}\n\n@{message.from_user.username}\n\n#id{message.from_user.id}", parse_mode="HTML")
    await message.answer('Сообщение было успешно отправлено администратору', reply_markup=kb)
    await state.clear()
    

@router.message(F.text == 'Добавить элемент')
async def add_element_user(message: Message, state: FSMContext):
    await state.set_state(Elements.add_element_user)
    await message.answer('Введите точное название элемента:', reply_markup=cancel_kb)

@router.message(StateFilter(Elements.add_element_user), F.text)
async def add_element_user(message: Message, state: FSMContext):
    y = await get_elements_by_user_telegram_id(str(message.from_user.id))
    if y:
        for element in y:
            if element.name == message.text:
                await message.answer('Элемент уже есть в вашей таблице!', reply_markup=cancel_kb)
                return
            
    x = await check_element_in_db(message.text)
    if x:
        element: Element = await create_element(1, message.text)
        user: User = await get_user_by_telegram_id(str(message.from_user.id))
    
        if user is None:
            await message.answer("Пользователь не найден.")
            await state.clear()
            return
        
        await add_element_to_user(str(user.telegram_id), str(element.name))
        
        if message.from_user.id in admins:
            await message.answer("Элемент успешно добавлен", reply_markup=adm_kb)
        else:
            await message.answer("Элемент успешно добавлен", reply_markup=kb)
    
    else:
        if message.from_user.id in admins:
            await message.answer("Элемент не опознан или название введено с ошибкой. Попробуйте еще раз", reply_markup=cancel_kb)
            return
        else:
            await message.answer("Элемент не опознан или название введено с ошибкой. Попробуйте еще раз", reply_markup=cancel_kb)
            return

    await state.clear()

@router.message(SupportedMediaFilter())
async def supported_media(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на медиафайлы от пользователя.
    Поддерживаются только типы, к которым можно добавить подпись (полный список см. в регистраторе внизу)

    :param message: медиафайл от пользователя
    :param l10n: объект локализации
    """
    if message.caption and len(message.caption) > 1000:
        return await message.reply(l10n.format_value("too-long-caption-error"))
    if message.from_user.id in banned:
        await message.answer(l10n.format_value("you-were-banned-error"))
    elif message.from_user.id in shadowbanned:
        return
    else:
        await message.copy_to(
            admin_chat_id,
            caption=((message.caption or "") + f"Вам пришло новое сообщение от пользователя! \n\n#id{message.from_user.id}"),
            parse_mode="HTML"
        )
        create_task(_send_expiring_notification(message, l10n))

@router.message()
async def unsupported_types(message: Message, l10n: FluentLocalization):
    """
    Хэндлер на неподдерживаемые типы сообщений, т.е. те, к которым нельзя добавить подпись

    :param message: сообщение от пользователя
    :param l10n: объект локализации
    """
    # Игнорируем служебные сообщения
    if message.content_type not in (
            ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER, ContentType.VIDEO_CHAT_STARTED,
            ContentType.VIDEO_CHAT_ENDED, ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED,
            ContentType.MESSAGE_AUTO_DELETE_TIMER_CHANGED, ContentType.NEW_CHAT_PHOTO, ContentType.DELETE_CHAT_PHOTO,
            ContentType.SUCCESSFUL_PAYMENT, "proximity_alert_triggered",  # в 3.0.0b3 нет поддержка этого контент-тайпа
            ContentType.NEW_CHAT_TITLE, ContentType.PINNED_MESSAGE):
        await message.reply(l10n.format_value("unsupported-message-type-error"))
    # await message.reply("SOme text")
