import asyncio

from openai import AsyncOpenAI, OpenAIError
from openai.types.beta import Thread

from settings import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    """
    Asynchronous client for interacting with OpenAI Assistants API.

    Provides methods to manage threads and communicate with assistants.
    """

    def __init__(self, openai_api_key: str, model: str, temperature: float):
        """
        Initializes the OpenAI async client.

        Args:
            openai_api_key (str): OpenAI API key.
            model (str): Model name to use for assistant responses (e.g. "gpt-3.5-turbo").
            temperature (float): Sampling temperature for response creativity.
        """
        self._client = AsyncOpenAI(api_key=openai_api_key)
        self._model = model
        self._temperature = temperature

    async def create_thread(self) -> Thread:
        """
        Creates a new thread for conversation.

        Returns:
            Thread: The created thread object.

        Raises:
            OpenAIError: If thread creation fails.
        """
        try:
            thread = await self._client.beta.threads.create()
            logger.info(f"Created thread with ID: {thread.id}")
            return thread
        except OpenAIError as e:
            logger.error(f"OpenAI Error (create_thread): {e}")
            raise

    async def retrieve_thread(self, thread_id: str) -> Thread:
        """
        Retrieves a thread by its ID.

        Args:
            thread_id (str): The ID of the thread to retrieve.

        Returns:
            Thread: The retrieved thread object.

        Raises:
            OpenAIError: If retrieval fails.
        """
        try:
            return await self._client.beta.threads.retrieve(thread_id=thread_id)
        except OpenAIError as e:
            logger.error(f"OpenAI Error (retrieve_thread): {e}")
            raise

    async def delete_thread(self, thread_id: str) -> bool:
        """
        Deletes a thread by its ID.

        Args:
            thread_id (str): The ID of the thread to delete.

        Returns:
            bool: True if deleted successfully, False otherwise.

        Raises:
            OpenAIError: If deletion fails.
        """
        try:
            await self._client.beta.threads.delete(thread_id=thread_id)
            logger.info(f"Deleted thread with ID: {thread_id}")
            return True
        except OpenAIError as e:
            logger.error(f"OpenAI Error (delete_thread): {e}")
            return False

    async def ask(self, assistant_id: str, thread_id: str, user_message: str, max_retries: int = 3) -> str:
        """
        Sends a user message to an assistant and retrieves the response.

        If there is an active run on the thread, it waits until it completes.
        Implements retry logic for transient server errors.

        Args:
            assistant_id (str): ID of the assistant to run.
            thread_id (str): ID of the conversation thread.
            user_message (str): User's message to send.
            max_retries (int): Number of retry attempts for failed runs.

        Returns:
            str: Assistant's reply as plain text.

        Raises:
            OpenAIError: If message creation or run execution fails.
        """
        try:
            runs = await self._client.beta.threads.runs.list(thread_id=thread_id, limit=1)
            latest_run = runs.data[0] if runs.data else None

            if latest_run and latest_run.status in ["queued", "in_progress"]:
                logger.info(f"Waiting for previous run {latest_run.id} to complete...")
                while latest_run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(1)
                    latest_run = await self._client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=latest_run.id
                    )
                if latest_run.status == "failed":
                    raise OpenAIError(f"Previous run failed: {latest_run.last_error}")

            await self._client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )

            for attempt in range(1, max_retries + 1):
                run = await self._client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=assistant_id,
                    model=self._model,
                    temperature=self._temperature
                )

                while run.status in ["queued", "in_progress"]:
                    await asyncio.sleep(1)
                    run = await self._client.beta.threads.runs.retrieve(
                        thread_id=thread_id,
                        run_id=run.id
                    )

                if run.status == "completed":
                    break

                if run.status == "failed":
                    error_code = getattr(run.last_error, "code", "")
                    error_msg = getattr(run.last_error, "message", "")
                    logger.warning(f"Run attempt {attempt} failed: {error_code} - {error_msg}")

                    if error_code == "server_error" and attempt < max_retries:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise OpenAIError(f"Run failed: {run.last_error}")

            messages = await self._client.beta.threads.messages.list(thread_id=thread_id)
            for message in messages.data:
                if message.role == "assistant":
                    for content in message.content:
                        if content.type == "text":
                            return content.text.value

            return ""

        except OpenAIError as e:
            logger.error(f"OpenAI Error (ask): {e}")
            raise
