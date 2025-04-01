## ✨ Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Assistant Setup](#assistant-setup)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)

---

## Overview

This project is a Telegram bot powered by the OpenAI Assistants API that supports multi-turn conversations with context preservation.

It offers two intelligent assistant modes:

- **Random Trivia GPT Assistant** — delivers fascinating and surprising technical facts from science, history, pop culture, and technology. Answers are concise, fun, and formatted with HTML to be visually engaging.
- **FactSpark GPT Assistant** — a short-response chatbot that answers user questions with 2–4 sentences, avoiding unnecessary introductions or verbose replies. Ideal for fast Q&A interactions.

Behind the scenes, the bot uses:
- **OpenAI Threads API** to maintain contextual conversations per user and mode.
- **SQLite** as a lightweight storage for threads and messages.
- **Custom assistant management CLI** for creating, listing, updating, and deleting assistants directly via terminal.

This design allows each Telegram user to have separate conversation threads for each interaction mode. You can also view full assistant histories or clear them if needed.

--- 


## Features

- **📚 Fact Mode**  
  Sends a short and surprising technical trivia fact from domains like science, history, culture, or technology. The assistant is trained to respond with fun, beginner-friendly facts using Telegram-compatible HTML formatting.

- **💬 GPT Mode**  
  Allows freeform chatting with a concise-response assistant. Replies are short (2–4 sentences), skip unnecessary introductions, and include HTML formatting (e.g. `<b>`, `<i>`, `<code>`) for a polished user experience.

- **🧠 Multi-turn Conversations**  
  Each user gets persistent threads for each mode. All messages are stored in a local **SQLite** database for context tracking and future retrieval, allowing seamless back-and-forth interaction.

- **🛠 Assistant Lifecycle via CLI**  
  A built-in command-line tool (`assistant_manager.py`) lets you easily create, update, list, or delete OpenAI Assistants. This makes it simple to manage prompt versions or test assistant behavior during development.

- **♻️ Robust Error Handling & Retry Logic**  
  Includes smart retrying for OpenAI API calls when temporary issues occur (e.g., server errors or parallel run conflicts), along with detailed logging for troubleshooting.

---


## Installation

Follow the steps below to set up the project locally.

### 1. Clone the repository

```bash
git clone https://github.com/wspjoy2011/smart_tg_bot.git
cd smart_tg_bot
```

### 2. Create and activate a virtual environment

<details>
<summary>Linux / macOS</summary>

```bash
python -m venv .venv
source .venv/bin/activate
```

</details>

<details>
<summary>Windows</summary>

```bash
python -m venv .venv
.venv\Scripts\activate
```

</details>

---

### 3. Install Poetry

If you don’t have [Poetry](https://python-poetry.org/) installed, you can install it with:

```bash
pip install poetry
```

---

### 4. Install project dependencies

```bash
poetry install
```

---

### 5. Configure environment variables

1. **Copy the sample file**:

   ```bash
   cp .env.sample .env
   ```

2. **Open `.env` and fill in your credentials**:

   ```env
   OPENAI_API_KEY=<your_openai_api_key>
   TG_BOT_API_KEY=<your_tg_bot_api_key>
   AI_ASSISTANT_RANDOM_FACTS_ID=<ID of assistant created with 'random.txt'>
   AI_ASSISTANT_FACT_SPARK_ID=<ID of assistant created with 'gpt.txt'>
   ```

---

### 6. Where to get the keys?

- 🔑 **OpenAI API Key**  
  Create an account or log in at [platform.openai.com](https://platform.openai.com/), then go to **API Keys** under your account settings and generate a key.

- 🤖 **Telegram Bot API Key**  
  Open [@BotFather](https://t.me/BotFather) in Telegram, use `/newbot`, and follow the prompts to create your bot and get the token.

- 🧠 **Assistant IDs**  
  After launching the bot, you must create two assistants (one for fun facts, one for chat) using the CLI tool (described in the next section). Their `id`s will be saved and used in the `.env` file.

---

## Assistant Setup

To interact with OpenAI Assistants, you first need to **create and configure assistants** via the included CLI tool.

> 📍 Navigate to the directory before running the CLI:
```bash
cd src/services/chatgpt
```

---

### ✅ Creating Assistants

You’ll need two assistants:
1. **FactSpark** – for concise GPT-style answers in `/gpt` mode.
2. **RandomFacts** – for surprising fact generation in `/random` mode.

Create a new assistant with:

```bash
python assistant_manager_cli.py --create -n "FactSpark" -p gpt
```

You will see the assistant ID in the console, for example:
```
Assistant created: asst_abc123456789 (FactSpark)
```

➡️ Copy this ID and paste it into your `.env` file:
```env
AI_ASSISTANT_FACT_SPARK_ID=asst_abc123456789
```

Repeat this process for the second assistant (e.g. `"RandomFacts"` with `-p random`).

---

### 🛠 CLI Usage

Run the assistant manager tool with any of the following options:

```bash
python assistant_manager_cli.py [OPTIONS]
```

#### Available Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and exit |
| `-l`, `--list` | List all existing assistants |
| `-c`, `--create` | Create a new assistant |
| `-n NAME`, `--name NAME` | Assistant name (required with `--create`) |
| `-p PROMPT`, `--prompt PROMPT` | Prompt filename from `resources/prompts` (required with `--create` or `--update`) |
| `-d ID`, `--delete ID` | Delete assistant by its ID |
| `-u ID`, `--update ID` | Update an assistant’s instructions by its ID |
| `-v`, `--version` | Show CLI tool version |

---

### 🔁 Examples

```bash
# List all assistants
python assistant_manager_cli.py --list

# Create assistant with name and prompt
python assistant_manager_cli.py --create -n "History Expert" -p history

# Update assistant’s instructions
python assistant_manager_cli.py --update asst_abc123456789 --prompt new_version

# Delete assistant
python assistant_manager_cli.py --delete asst_abc123456789
```

---

## Usage

To run the bot:

```bash
$ poetry run python src/main.py
```

---

### 💬 Interacting with the Bot

Once the bot is running:

- Open Telegram and find your bot using the `@YourBotUsername`
- Press **Start** or send the `/start` command to initialize the session
- You’ll see an interactive menu with buttons for different modes:
  - 🧠 **GPT**: chat with an assistant trained to give short, precise answers (uses the FactSpark assistant)
  - 🎲 **Random Fact**: receive surprising technical facts (uses the RandomFacts assistant)

---

### 🧵 Conversation Persistence

- Each user and mode (e.g. `/gpt`, `/random`) has a dedicated **OpenAI thread**
- All user messages and assistant replies are stored in a local **SQLite database**
- When you return to a mode later, the conversation context is preserved
- Multi-turn interactions with memory are possible thanks to OpenAI’s **Assistant Threads**

---

### 🛑 Stop and Restart

You can stop the bot at any time (Ctrl+C), and restart it without losing prior chat history. Each assistant thread will continue from where the user left off.

---


## Project Structure

```
.
├── README.md                  # Project documentation
├── poetry.lock / pyproject.toml  # Poetry dependency and project configuration files
├── .env.sample                # Example of environment configuration file
├── storage/
│   └── chat_sessions.db       # SQLite database storing threads and message history
├── logs/
│   └── app.log                # Application log output
├── resources/                # Static content used by the bot
│   ├── images/               # Images shown in the bot's UI per mode (main, gpt, random)
│   ├── menus/                # JSON files defining inline button menus
│   ├── messages/             # HTML welcome messages for each mode
│   └── prompts/              # Prompt templates used to instruct OpenAI assistants
├── src/                      # Main application source code
│   ├── main.py               # Entry point to launch the bot
│   ├── bot/                  # Telegram bot logic
│   │   ├── commands.py       # Command handlers for /start, /random, /gpt
│   │   ├── handlers/         # Async message handlers (e.g. for GPT mode)
│   │   ├── keyboards.py      # Functions to build inline keyboard markup
│   │   └── resource_loader.py # Load messages, menus, and images from files
│   ├── db/                   # Database-related modules
│   │   ├── repository.py     # Database repository for threads and messages
│   │   ├── enums.py          # Enum definitions (SessionMode, MessageRole)
│   │   └── initializer.py    # Initializes the SQLite database schema
│   ├── services/             # External service integration (OpenAI)
│   │   └── chatgpt/
│   │       ├── client.py     # Async OpenAI API client (thread management, completions)
│   │       └── assistant_manager_cli.py  # CLI tool for managing assistants (create, delete, update)
│   └── settings/
│       ├── config.py         # Reads settings and env variables using Pydantic
│       └── logging_config.py # Logging setup and logger creation
```

---


## Tech Stack

This project is built with a modern asynchronous Python stack and integrates several key technologies:

### 🧠 Core Libraries

- **OpenAI Python SDK**  
  Used to interact with the OpenAI Assistants API (chat completions, thread management, message history).

- **python-telegram-bot**  
  Powerful and fully asynchronous framework for building Telegram bots.

- **aiosqlite**  
  Lightweight async wrapper for SQLite, used to store OpenAI thread IDs and full message history per user/mode.

- **aiofiles**  
  Async file I/O support, used for loading images, HTML messages, and prompt templates.

### ⚙️ Configuration & Environment

- **pydantic-settings**  
  Manages and validates environment variables with type hints.

- **python-dotenv**  
  Loads environment variables from `.env` files during development.

- **argparse**  
  Built-in Python library used for building the CLI tool to manage assistants (create, update, delete).

### 📦 Dependency Management

- **Poetry**  
  Handles virtual environments and dependency/version management in a clean and reproducible way.
 