import json

import aiofiles

from settings import config


async def load_message(name: str) -> str:
    """
    Loads an HTML-formatted message from the messages' directory.

    Args:
        name (str): The base filename (without extension) of the HTML message to load.

    Returns:
        str: The contents of the HTML file as a string.
    """

    path = config.path_to_messages / f"{name}.html"
    async with aiofiles.open(path, mode="r", encoding="utf-8") as file:
        return await file.read()


async def load_image(name: str) -> bytes:
    """
    Loads an image as bytes from the images directory.

    Args:
        name (str): The base filename (without extension) of the image to load.

    Returns:
        bytes: The image content in bytes, suitable for sending to Telegram.
    """
    path = config.path_to_images / f"{name}.jpg"
    async with aiofiles.open(path, mode="rb") as file:
        return await file.read()


async def load_menu(name: str) -> dict:
    """
    Loads a JSON menu definition from the menus' directory.

    Args:
        name (str): The base filename (without extension) of the menu JSON to load.

    Returns:
        dict: The parsed JSON content as a dictionary of command-label pairs.
    """
    path = config.path_to_menus / f"{name}.json"
    async with aiofiles.open(path, encoding="utf-8") as file:
        content = await file.read()
        return json.loads(content)


async def load_prompt(name: str) -> str:
    """
    Loads a text prompt from the prompts' directory.

    Args:
        name (str): The base filename (without extension) of the prompt file.

    Returns:
        str: The contents of the prompt file as a string.
    """
    path = config.path_to_prompts / f"{name}.txt"
    async with aiofiles.open(path, mode="r", encoding="utf-8") as file:
        return await file.read()
