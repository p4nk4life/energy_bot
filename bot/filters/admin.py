from aiogram.filters import Filter
from aiogram.types import Message, ContentType
from typing import List
from bot.config_reader import admin_chat_id
from aiogram.types import Message

#попытка №1
class AdminFilter(Filter):
    def __init__(self, admins) -> None:
        self.admins = admin_chat_id.split(',')

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in self.admins:
            return True
        return False

#попытка №2
async def is_superuser(message: Message, superusers: list[int]) -> bool:
    return str(message.from_user.id) in superusers
