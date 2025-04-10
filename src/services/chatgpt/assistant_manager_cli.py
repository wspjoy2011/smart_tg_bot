import sys
from pathlib import Path

import argparse
from openai import OpenAIError

from tabulate import tabulate

current_dir = Path(__file__).resolve()
src_dir = current_dir.parents[2]
sys.path.insert(0, str(src_dir))

from services.chatgpt.assistant_manager import AssistantManager
from settings import config


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
            "  python assistant_manager_cli.py --list\n"
            "  python assistant_manager_cli.py --list 20\n"
            "  python assistant_manager_cli.py --create -n \"History Expert\" -p history\n"
            "  python assistant_manager_cli.py --delete asst_abc123\n"
            "  python assistant_manager_cli.py --update asst_abc123 -p updated_prompt\n"
            "  python assistant_manager_cli.py --show asst_abc123\n"
            "  python assistant_manager_cli.py --show asst_abc123 --instructions\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-l", "--list",
        nargs="?",
        const=10,
        type=int,
        metavar="N",
        help="List existing assistants (default: 10). Optionally specify a number: --list 20"
    )

    parser.add_argument(
        "-s", "--show",
        type=str,
        metavar="ASSISTANT_ID",
        help="Show full details of an assistant by its ID"
    )

    parser.add_argument(
        "--instructions",
        action="store_true",
        help="Show full assistant instructions when using --show"
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
    - Listing assistants with optional limit (--list [N])
    - Showing detailed assistant info (--show ASSISTANT_ID)
      with optional full instructions output (--instructions)
    - Creating new assistants from prompt templates (--create -n NAME -p PROMPT)
    - Updating assistant instructions from prompt templates (--update ASSISTANT_ID -p PROMPT)
    - Deleting assistants by ID (--delete ASSISTANT_ID)

    Usage examples:
    - List top 10 assistants (default):      python assistant_manager.py --list
    - List 25 assistants:                    python assistant_manager.py --list 25
    - Show details of an assistant:          python assistant_manager.py --show asst_abc123
    - Show assistant + full instructions:    python assistant_manager.py --show asst_abc123 --instructions
    - Create new assistant from prompt:      python assistant_manager.py --create -n "Quiz" -p quiz
    - Update assistant with new prompt:      python assistant_manager.py --update asst_abc123 -p quiz_v2
    - Delete assistant by ID:                python assistant_manager.py --delete asst_abc123
    """
    args = parse_args()

    manager = AssistantManager(
        api_key=config.openai_api_key,
        model=config.openai_model
    )

    if args.list:
        limit = args.list or 10
        assistants = manager.list_assistants(limit=limit)

        if not assistants:
            print("No assistants found.")
        else:
            rows = [(a.id, a.name) for a in assistants]
            print(tabulate(rows, headers=["ID", "Name"], tablefmt="github"))


    elif args.show:
        try:
            assistant = manager.get_assistant_details(args.show)
        except OpenAIError as e:
            print(f"Failed to retrieve assistant: {e}")
            return

        rows = [
            ["ID", assistant.id],
            ["Name", assistant.name or "—"],
            ["Model", assistant.model],
            ["Created At", assistant.created_at],
            ["Description", assistant.description or "—"],
            ["Instructions", (assistant.instructions[:120] + "...") if assistant.instructions and len(
                assistant.instructions) > 120 else assistant.instructions or "—"],
            ["Tools", ", ".join(tool.type for tool in assistant.tools) if assistant.tools else "None"],
            ["Temperature", str(assistant.temperature) if assistant.temperature is not None else "Default"],
            ["Top P", str(assistant.top_p) if assistant.top_p is not None else "Default"],
        ]

        print(tabulate(rows, headers=["Field", "Value"], tablefmt="fancy_grid"))

        if args.instructions and assistant.instructions:
            print("\nFull Instructions:\n")
            print(assistant.instructions)

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
