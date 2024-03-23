from db import create_user, add_element_to_user, create_element, get_elements_by_user_telegram_id
import asyncio


async def main():
    # TODO: fix this shit
    get_user = await get_elements_by_user_telegram_id(123)
    print(get_user)
    # user = await create_user("kill_your_soul", "1337", 123)
    # element = await create_element(1,"First", "test")
    # print(user)


if __name__ == '__main__':
    asyncio.run(main())
