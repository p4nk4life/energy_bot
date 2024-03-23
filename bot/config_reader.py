import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import SecretStr

from logging import info

token = os.environ.get("bot_token")
admin_chat_id = os.environ.get("ADMIN_CHAT_ID")

# class Settings(BaseSettings):
#     bot_token: SecretStr
#     admin_chat_id: int
#     remove_sent_confirmation: bool
#     webhook_domain: Optional[str]
#     webhook_path: Optional[str]
#     app_host: Optional[str] = "0.0.0.0"
#     app_port: Optional[int] = 9000
#     custom_bot_api: Optional[str]
#
#     class Config:
#         env_file = '.env'
#         env_file_encoding = 'utf-8'
#         env_nested_delimiter = '__'
#
#
# config = Settings()
