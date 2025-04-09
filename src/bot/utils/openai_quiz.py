import json

from openai import OpenAIError

from services import OpenAIClient
from settings import get_logger

logger = get_logger(__name__)


async def ask_quiz_with_retries(
    assistant_id: str,
    thread_id: str,
    user_message: str,
    openai_client: OpenAIClient,
    max_attempts: int = 2
) -> tuple[str, list[dict]]:
    """
    Sends a quiz generation request to the assistant with retry logic for JSON and API errors.

    This function attempts to send a prompt to the OpenAI assistant to generate quiz questions.
    It retries up to `max_attempts` times in case of OpenAI API errors, JSON decoding issues, or
    invalid response formats.

    Args:
        assistant_id (str): The ID of the assistant to query.
        thread_id (str): The OpenAI thread ID associated with the user session.
        user_message (str): The quiz generation prompt to send.
        openai_client (OpenAIClient): The client used to communicate with OpenAI API.
        max_attempts (int, optional): Maximum number of attempts in case of failure. Defaults to 2.

    Returns:
        tuple[str, list[dict]]: A tuple containing the raw response string
        and the parsed quiz data as a list of dictionaries.

    Raises:
        RuntimeError: If all attempts fail due to API errors, invalid JSON, or incorrect data format.
    """
    for attempt in range(1, max_attempts + 1):
        try:
            response = await openai_client.ask(
                assistant_id=assistant_id,
                thread_id=thread_id,
                user_message=user_message
            )
        except OpenAIError as e:
            logger.error(f"OpenAI Error on quiz prompt, attempt {attempt}: {e}")
            if attempt == max_attempts:
                raise RuntimeError("Failed to generate quiz due to OpenAI error.")
            continue

        try:
            quiz_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error on quiz prompt, attempt {attempt}: {e}")
            if attempt == max_attempts:
                raise RuntimeError("Received invalid JSON format for quiz.")
            continue

        if not isinstance(quiz_data, list) or not quiz_data:
            logger.error(f"Invalid quiz format received, attempt {attempt}")
            if attempt == max_attempts:
                raise RuntimeError("Quiz data is invalid or empty.")
            continue

        return response, quiz_data

    raise RuntimeError("Unknown failure in quiz request.")
