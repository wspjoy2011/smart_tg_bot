from typing import Optional, List

from openai import OpenAI, OpenAIError
from openai.types.beta import Assistant

from settings import get_logger

logger = get_logger(__name__)


class AssistantManager:
    """A manager class to handle OpenAI Assistant operations (create, list, update, delete)."""

    def __init__(self, api_key: str, model: str):
        """
        Initializes the OpenAI client.

        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI model name.
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def create_assistant(
            self,
            name: str,
            instructions: str,
            tools: Optional[list] = None
    ) -> Assistant:
        """
        Creates a new OpenAI Assistant.

        Args:
            name (str): Assistant name.
            instructions (str): Prompt/instructions text.
            tools (Optional[list]): Optional list of tools (default is empty list).

        Returns:
            Assistant: The created Assistant object.
        """
        tools = tools or []

        assistant = self.client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=self.model
        )
        return assistant

    def list_assistants(self, limit: int = 10) -> List[Assistant]:
        """
        Lists existing assistants.

        Args:
            limit (int): Number of assistants to return.

        Returns:
            List[Assistant]: List of assistant objects.
        """
        assistants_page = self.client.beta.assistants.list(limit=limit)
        return assistants_page.data

    def update_assistant(self, assistant_id: str, instructions: str) -> Assistant:
        """
        Updates instructions of an existing assistant.

        Args:
            assistant_id (str): ID of the assistant to update.
            instructions (str): New instructions text.

        Returns:
            Assistant: The updated Assistant object.

        Raises:
            OpenAIError: If updating fails.
        """
        try:
            updated_assistant = self.client.beta.assistants.update(
                assistant_id=assistant_id,
                instructions=instructions
            )
        except OpenAIError as e:
            logger.error(f"OpenAI Error: Failed to update assistant {assistant_id}: {e}")
            raise
        else:
            return updated_assistant

    def delete_assistant(self, assistant_id: str) -> bool:
        """
        Deletes an assistant by ID.

        Args:
            assistant_id (str): ID of the assistant to delete.

        Returns:
            bool: True if successful.

        Raises:
            OpenAIError: If deletion fails.
        """
        try:
            self.client.beta.assistants.delete(assistant_id)
            return True
        except OpenAIError as e:
            logger.error(f"OpenAI Error: failed to delete assistant {assistant_id}: {e}")
            raise

    def get_assistant_details(self, assistant_id: str) -> Assistant:
        """
        Retrieves detailed information about an assistant by ID.

        Args:
            assistant_id (str): ID of the assistant to retrieve.

        Returns:
            Assistant: Assistant object with full details.

        Raises:
            OpenAIError: If retrieval fails.
        """
        try:
            return self.client.beta.assistants.retrieve(assistant_id)
        except OpenAIError as e:
            logger.error(f"OpenAI Error: Failed to retrieve assistant {assistant_id}: {e}")
            raise
