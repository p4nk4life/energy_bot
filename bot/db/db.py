import os
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.future import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from bot.db.models import User, Element, UserElementLink, AdminElement
from sqlalchemy.orm import sessionmaker
from typing import Optional, List
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from logging import info
from sqlalchemy import update, delete

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/dev"

# async_engine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

async_engine = create_async_engine(DATABASE_URL, echo=False, future=True)


async def init_db():
    async with async_engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


def async_session_generator():
    return async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_session():
    try:
        async_session = async_session_generator()
        async with async_session() as session:
            return session
    except:
        raise
    # async with async_session() as session:
    #     yield session

# TODO:check user existance
async def create_user(
        username: str, number: Optional[str] = None, telegram_id: Optional[str] = None
) -> User:
    db = await get_session()
    # print(session)
    # db = None
    # async with db().__anext__() as session:
    return await _create_user(db, username, number, telegram_id)


async def _create_user(
        db: AsyncSession,
        username: str,
        number: Optional[str] = None,
        telegram_id: Optional[str] = None,
) -> User:
    new_user = User(username=username, number=number, telegram_id=telegram_id)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    await db.close()
    return new_user


async def _get_element_by_id(element_id: int) -> Element:
    db = await get_session()
    stmt = select(Element).where(Element.element_id == element_id)
    res = await db.execute(stmt)
    element: Element = res.scalar()
    await db.close()
    return element


async def get_user_by_telegram_id(telegram_id: str):
    db = await get_session()
    user = await _get_user_by_telegram_id(db, telegram_id)
    await db.close()
    return user


async def _get_user_by_telegram_id(db: AsyncSession, telegram_id: str):
    stmt = select(User).where(User.telegram_id == telegram_id)
    print(stmt)
    res = await db.execute(stmt)
    user = res.scalar()
    await db.close()
    return user


async def add_element_to_user(user_id: str, element_name: str) -> bool:
    db = await get_session()
    return await _add_element_to_user(db, user_id, element_name)


async def _add_element_to_user(db: AsyncSession, user_id: str, element_name: str) -> bool:
    user: User = await get_user_by_telegram_id(user_id)
    element: Element = await _get_element_by_name(element_name)
    user_element_link = UserElementLink(user=user, element=element)
    db.add(user_element_link)
    await db.commit()
    await db.refresh(user_element_link)
    await db.close()
    return True


async def create_element(element_id: int, name: str, comment: Optional[str] = None) -> Element:
    db = await get_session()
    return await _create_element(db, element_id, name, comment)


async def _create_element(db: AsyncSession, element_id: int, name: str,
                          comment: Optional[str] = None) -> Element | None:
    new_element = Element(element_id=element_id, name=name, comment=comment)
    elements_res = await db.execute(select(AdminElement))
    elements: list[AdminElement] = elements_res.scalars().all()
    for element in elements:
        if name == element.name:
            new_element.element_id = element.element_id
            new_element.comment = element.comment
            db.add(new_element)
            await db.commit()
            await db.refresh(new_element)
            await db.close()
            return new_element
    return None


async def get_elements_by_user_telegram_id(telegram_id: str):
    db = await get_session()
    elements = await _get_elements_by_user_telegram_id(db, telegram_id)
    await db.close()
    return elements


async def _get_elements_by_user_telegram_id(
        db: AsyncSession,
        telegram_id: str
) -> Optional[List[Element]]:
    # Получаем пользователя по telegram_id
    user = await get_user_by_telegram_id(telegram_id)

    # user = await session.exec(select(User).where(User.telegram_id == telegram_id))

    if user:
        # Получаем все элементы для этого пользователя
        elements_result = await db.exec(
            select(Element)
            .join(UserElementLink)
            .where(UserElementLink.user_id == user.id)
        )
        elements = elements_result.scalars().all()
        await db.close()
        return elements
    else:
        await db.close()
        return None


async def add_element_to_admin_table(id_: int, name: str, comment: str) -> AdminElement:
    db = await get_session()
    admin_element = await _add_element_to_admin_table(db, id_, name, comment)
    return admin_element


async def _add_element_to_admin_table(db: AsyncSession, id_: int, name: str, comment: str) -> AdminElement:
    admin_element: AdminElement = AdminElement(element_id=id_, name=name, comment=comment)
    db.add(admin_element)
    await db.commit()
    await db.refresh(admin_element)
    await db.close()
    return admin_element


async def delete_admin_element(id_: int):
    db = await get_session()
    return await _delete_admin_element(db, id_)


async def check_user(telegram_id: str) -> bool:
    db = await get_session()
    x = await db.exec(select(User).where(User.telegram_id == telegram_id))
    result = x.scalar()
    info(result)
    await db.close()
    return bool(result)   


async def _delete_admin_element(db: AsyncSession, id_: int) -> bool:
    # admin_element: AdminElement | None = await db.get(AdminElement, id_)
    # admin_element_ = await db.execute(select(AdminElement).where(AdminElement.element_id == id_))
    admin_element_result = await db.exec(
        select(AdminElement)
        .where(AdminElement.element_id == id_)
    )
    admin_element = admin_element_result.scalar()
    info(f'admin_element: {admin_element}')
    if admin_element:
        await db.delete(admin_element)
        await db.commit()
        return True
    await db.close()
    return False

async def check_element_in_db(element_name: str) -> bool:
    db = await get_session()
    return await _check_element_in_db(db, element_name)

async def _check_element_in_db(db: AsyncSession, element_name: str) -> bool:
    admin_elements_result = await db.exec(select(AdminElement))
    admin_elements = admin_elements_result.scalars().all()
    info(admin_elements)
    for element in admin_elements:
        if element.name == element_name:
            info(element.name)
            return True         
    return False

async def check_element_in_db_by_id(element_id: int) -> bool:
    db = await get_session()
    return await _check_element_in_db_by_id(db, element_id)

async def _check_element_in_db_by_id(db: AsyncSession, element_id: int) -> bool:
    admin_elements_result = await db.exec(select(AdminElement))
    admin_elements = admin_elements_result.scalars().all()
    for element in admin_elements:
        if element.element_id == element_id:
            return True         
    return False

async def _get_element_by_name(element_name: str) -> Element:
    db = await get_session()
    stmt = select(Element).where(Element.name == element_name)
    res = await db.execute(stmt)
    element: Element = res.scalar()
    await db.close()
    return element

async def get_all_admin_elements() -> List[AdminElement]:
    db = await get_session()
    admin_elements_result = await db.exec(select(AdminElement))
    admin_elements: List[AdminElement] = admin_elements_result.scalars().all()
    await db.close()
    return admin_elements

async def update_admin_elements(new_elements):
    db = await get_session()
    try:
        # Получаем все текущие элементы из базы
        current_elements_result = await db.execute(select(AdminElement))
        current_elements = current_elements_result.scalars().all()
        
        # Преобразуем список новых элементов в словарь для удобства поиска
        new_elements_dict = {el[0]: el[1] for el in new_elements}

        # Обновляем существующие элементы и добавляем новые
        for el_id, name in new_elements_dict.items():
            # Проверяем, существует ли элемент с таким ID
            exists = await db.execute(select(AdminElement).where(AdminElement.element_id == el_id))
            if exists.scalar():
                # Если элемент существует, обновляем его имя, если оно отличается
                await db.execute(
                    update(AdminElement)
                    .where(AdminElement.element_id == el_id)
                    .values(name=name)
                )
            else:
                # Если элемент новый, добавляем его в базу
                new_element = AdminElement(element_id=el_id, name=name)
                db.add(new_element)
        
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Ошибка при обновлении элементов: {e}")
    finally:
        await db.close()


async def remove_user_elements(user_telegram_id: str, element_names_to_remove):
    db = await get_session()
    try:
        user = await get_user_by_telegram_id(user_telegram_id)
        # Находим все элементы пользователя, которые нужно удалить
        for name in element_names_to_remove:
            element = await db.execute(
                select(Element).where(Element.name == name)
            )
            element = element.scalars().first()
            if element:
                await db.execute(
                    delete(UserElementLink)
                    .where(UserElementLink.user_id == user.id, UserElementLink.element_id == element.id)
                )
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"Ошибка при удалении элементов пользователя: {e}")
    finally:
        await db.close()