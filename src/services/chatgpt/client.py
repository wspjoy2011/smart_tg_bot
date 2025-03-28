from openai import AsyncOpenAI, OpenAIError
from openai.types.beta import Thread

from settings import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    def __init__(self, openai_api_key: str, model: str, temperature: float):
        self._client = AsyncOpenAI(api_key=openai_api_key)
        self._model = model
        self._temperature = temperature

    async def create_thread(self) -> Thread:
        try:
            thread = await self._client.beta.threads.create()
            logger.info(f"Created thread with ID: {thread.id}")
            return thread
        except OpenAIError as e:
            logger.error(f"OpenAI Error (create_thread): {e}")
            raise

    async def retrieve_thread(self, thread_id: str) -> Thread:
        try:
            return await self._client.beta.threads.retrieve(thread_id=thread_id)
        except OpenAIError as e:
            logger.error(f"OpenAI Error (retrieve_thread): {e}")
            raise

    async def delete_thread(self, thread_id: str) -> bool:
        try:
            await self._client.beta.threads.delete(thread_id=thread_id)
            logger.info(f"Deleted thread with ID: {thread_id}")
            return True
        except OpenAIError as e:
            logger.error(f"OpenAI Error (delete_thread): {e}")
            return False

    async def ask(self, assistant_id: str, thread_id: str, user_message: str) -> str:
        try:
            await self._client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_message
            )

            run = await self._client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                model=self._model,
                temperature=self._temperature
            )

            while run.status in ["queued", "in_progress"]:
                run = await self._client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

            if run.status == "failed":
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
