from openai import AsyncOpenAI, OpenAIError

from settings import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    def __init__(self, openai_api_key: str, model: str, temperature: float):
        self._client = AsyncOpenAI(api_key=openai_api_key)
        self._model = model
        self._temperature = temperature

    async def ask(self, user_message: str, system_prompt: str) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=self._temperature
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            logger.error(f"OpenAI Error: {e}")
            raise
