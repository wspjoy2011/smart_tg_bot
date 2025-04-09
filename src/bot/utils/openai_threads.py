from db.repository import GptThreadRepository
from services import OpenAIClient


async def get_or_create_thread_id(
        tg_user_id: int,
        mode: str,
        thread_repository: GptThreadRepository,
        openai_client: OpenAIClient
) -> str:
    """
    Retrieves an existing OpenAI thread ID or creates a new one if not found.

    Args:
        tg_user_id (int): Telegram user ID.
        mode (str): Session mode (e.g., "gpt", "quiz").
        thread_repository (GptThreadRepository): Thread repository instance.
        openai_client (OpenAIClient): OpenAI client to create threads.

    Returns:
        str: Valid OpenAI thread ID.
    """
    thread_id = await thread_repository.get_thread_id(tg_user_id, mode)
    if thread_id is None:
        thread = await openai_client.create_thread()
        thread_id = thread.id
        await thread_repository.create_thread(tg_user_id, mode, thread_id)
    return thread_id
