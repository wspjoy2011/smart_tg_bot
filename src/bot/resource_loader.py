import json

import aiofiles

from settings import config


async def load_message(name: str) -> str:
    path = config.path_to_messages / f"{name}.html"
    async with aiofiles.open(path, mode="r", encoding="utf-8") as file:
        return await file.read()


async def load_image(name: str) -> bytes:
    path = config.path_to_images / f"{name}.jpg"
    async with aiofiles.open(path, mode="rb") as file:
        return await file.read()


async def load_menu(name: str) -> dict:
    path = config.path_to_menus / f"{name}.json"
    async with aiofiles.open(path, encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)


async def load_prompt(name: str) -> str:
    path = config.path_to_prompts / f"{name}.txt"
    async with aiofiles.open(path, mode="r", encoding="utf-8") as file:
        return await file.read()
