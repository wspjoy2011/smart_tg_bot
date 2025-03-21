import asyncio
import os

from openai import AsyncOpenAI, OpenAIError

from config import OPENAI_API_KEY


class OpenAIClient:
    def __init__(self):
        self._client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    async def ask(self, user_message: str, system_prompt: str = "You are a helpful assistant.") -> str:
        try:
            response = await self._client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ]
            )
            return response.choices[0].message.content
        except OpenAIError as e:
            # logging
            raise


async def main():
    client = OpenAIClient()

    reply = await client.ask("Hi, whats up?")

    print(reply)


if __name__ == '__main__':
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
























