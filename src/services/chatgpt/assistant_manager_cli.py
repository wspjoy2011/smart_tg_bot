import sys
from pathlib import Path

import argparse
from openai import OpenAI, OpenAIError
from openai.types.beta import Assistant
from typing import Optional, List

current_dir = Path(__file__).resolve()
src_dir = current_dir.parents[1].parent
sys.path.insert(0, str(src_dir))

from settings import config, get_logger

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


def parse_args():
    """
    Parses CLI arguments using argparse.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(
        prog="assistant-manager",
        description=(
            "Manage your OpenAI Assistants\n\n"
            "Examples:\n"
            "  python assistant_manager.py --list\n"
            "  python assistant_manager.py --create -n \"History Expert\" -p history\n"
            "  python assistant_manager.py --delete asst_abc123\n"
            "  python assistant_manager.py --update asst_abc123 -p updated_prompt\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List existing assistants"
    )

    parser.add_argument(
        "-c", "--create",
        action="store_true",
        help="Create a new assistant"
    )

    parser.add_argument(
        "-n", "--name",
        type=str,
        help="Name of the assistant (required for --create)"
    )

    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="Prompt filename without extension (required for --create)"
    )

    parser.add_argument(
        "-d", "--delete",
        type=str,
        metavar="ASSISTANT_ID",
        help="Delete an assistant by its ID"
    )

    parser.add_argument(
        "-u", "--update",
        type=str,
        metavar="ASSISTANT_ID",
        help="Update an assistant's instructions by its ID"
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="assistant-manager 1.0.0",
        help="Show program version"
    )

    return parser.parse_args()


def load_prompt(name: str) -> str:
    """
    Loads prompt text from a .txt file by name.

    Args:
        name (str): Prompt file name (without extension).

    Returns:
        str: Contents of the prompt file.

    Raises:
        FileNotFoundError: If the prompt file is missing.
    """
    path = config.path_to_prompts / f"{name}.txt"
    with open(path, mode="r", encoding="utf-8") as file:
        return file.read()


def main():
    """
    Entry point for the assistant manager CLI tool.

    Based on the parsed CLI arguments, performs actions like:
    - Listing assistants
    - Creating new assistants from prompt templates
    - Updating instructions
    - Deleting assistants
    """
    args = parse_args()

    manager = AssistantManager(
        api_key=config.openai_api_key,
        model=config.openai_model
    )

    if args.list:
        assistants = manager.list_assistants()
        if not assistants:
            print("No assistants found.")
        for assistant in assistants:
            print("#" * 50)
            print(f"\nID: {assistant.id}")
            print(f"Name: {assistant.name}")
            print(f"Instructions: {assistant.instructions}")
            print("#" * 50)

    elif args.create:
        if not args.name or not args.prompt:
            print("Error: --name and --prompt are required for creating an assistant.")
            print("Use -h for help.")
            return

        try:
            prompt_text = load_prompt(args.prompt)
        except FileNotFoundError:
            print(f"Error: Prompt file '{args.prompt}.txt' not found in prompts directory.")
            return

        assistant = manager.create_assistant(
            name=args.name,
            instructions=prompt_text
        )
        print(f"Assistant created: {assistant.id} ({assistant.name})")

    elif args.delete:
        try:
            manager.delete_assistant(args.delete)
        except OpenAIError as e:
            print(e)
        else:
            print(f"Assistant {args.delete} deleted successfully.")

    elif args.update:
        if not args.prompt:
            print("Error: --prompt is required for updating an assistant.")
            print("Use -h for help.")
            return

        try:
            prompt_text = load_prompt(args.prompt)
        except FileNotFoundError:
            print(f"Error: Prompt file '{args.prompt}.txt' not found in prompts directory.")
            return

        try:
            updated = manager.update_assistant(args.update, prompt_text)
            print(f"Assistant {updated.id} ({updated.name}) updated successfully.")
        except OpenAIError as e:
            print(f"Failed to update assistant: {e}")
    else:
        print("No valid options provided. Use 'python assistant_manager.py -h' to see available commands.")


if __name__ == "__main__":
    main()
