from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from bot.keyboards import get_quiz_answer_keyboard
from bot.utils.openai_quiz import ask_quiz_with_retries
from bot.utils.openai_threads import get_or_create_thread_id
from bot.utils.quiz import (
    evaluate_answer,
    store_quiz_interaction,
    show_next_question,
    show_final_result,
)
from db.enums import SessionMode, MessageRole
from db.repository import GptThreadRepository
from services import OpenAIClient
from settings import config, get_logger

logger = get_logger(__name__)


async def handle_quiz_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles the user's quiz topic selection from inline buttons.

    Sends a prompt to OpenAI to generate a new quiz based on the selected topic,
    ensures a thread exists for the user, retries on failure, and stores the quiz state.
    Displays the first question with answer buttons.

    Args:
        update (telegram.Update): The update triggered by a callback query.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object containing bot data and user session state.

    Raises:
        RuntimeError: If OpenAI fails to respond or returns invalid JSON after retries.

    Side Effects:
        - Creates or reuses an OpenAI thread.
        - Saves user query and assistant reply to the database.
        - Saves quiz questions and state to context.user_data.
        - Sends the first question and answer options to the user.
    """
    mode = context.user_data.get("mode")
    if mode != SessionMode.QUIZ.value:
        return

    query = update.callback_query
    await query.answer()

    topic = query.data.replace("quiz_", "")
    tg_user_id = query.from_user.id

    openai_client: OpenAIClient = context.bot_data["openai_client"]
    thread_repository: GptThreadRepository = context.bot_data["thread_repository"]

    thread_id = await get_or_create_thread_id(tg_user_id, mode, thread_repository, openai_client)

    user_message = (f"Please generate a new unique set of 10 quiz questions on the topic: {topic}."
                    f" Do not repeat previous questions in this thread.")

    await thread_repository.add_message(thread_id, role=MessageRole.USER.value, content=user_message)

    assistant_id = config.ai_assistant_quiz_master_id

    try:
        quiz_response, quiz_data = await ask_quiz_with_retries(
            assistant_id=assistant_id,
            thread_id=thread_id,
            user_message=user_message,
            openai_client=openai_client
        )
    except RuntimeError as e:
        logger.error(f"Quiz generation failed for topic '{topic}': {e}")
        await query.edit_message_text(str(e))
        return

    context.user_data["quiz"] = {
        "questions": quiz_data,
        "current": 0,
        "score": 0
    }

    first_question = quiz_data[0]["question"]
    options = quiz_data[0]["options"]

    await query.edit_message_text(
        f"<b>Question 1:</b>\n{first_question}",
        parse_mode="HTML"
    )

    await context.bot.send_message(
        chat_id=query.message.chat.id,
        text="Choose your answer:",
        reply_markup=get_quiz_answer_keyboard(options)
    )

    await thread_repository.add_message(
        thread_id, role=MessageRole.ASSISTANT.value, content=quiz_response
    )


async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processes the user's answer to a quiz question.

    Compares the answer to the correct one, updates the score, saves the exchange to the database,
    and either moves to the next question or completes the quiz.

    Args:
        update (telegram.Update): The incoming message update containing the user's answer.
        context (telegram.ext.ContextTypes.DEFAULT_TYPE): The context object containing user session and bot data.

    Side Effects:
        - Sends feedback to the user on whether the answer was correct.
        - Increments score if the answer is correct.
        - Stores the interaction in the database.
        - Presents the next question or final result.
        - Removes quiz state from context.user_data after completion.
    """
    if context.user_data.get("mode") != SessionMode.QUIZ.value:
        return

    tg_user_id = update.effective_user.id
    user_answer = update.message.text.strip()

    quiz_state = context.user_data.get("quiz")
    if not quiz_state:
        await update.message.reply_text(
            "No active quiz found. Please select a quiz topic to start.",
            reply_markup=ReplyKeyboardRemove()
        )
        return

    current_idx = quiz_state["current"]
    questions = quiz_state["questions"]
    current_question = questions[current_idx]
    correct_answer = current_question["answer"]

    feedback, is_correct = evaluate_answer(user_answer, correct_answer)
    if is_correct:
        quiz_state["score"] += 1

    thread_repo: GptThreadRepository = context.bot_data["thread_repository"]
    thread_id = await thread_repo.get_thread_id(tg_user_id, SessionMode.QUIZ.value)
    await store_quiz_interaction(thread_repo, thread_id, user_answer, feedback)

    quiz_state["current"] += 1
    current_idx = quiz_state["current"]

    if current_idx < len(questions):
        next_question = questions[current_idx]
        reply_markup = get_quiz_answer_keyboard(next_question["options"])
        await show_next_question(update, feedback, next_question, current_idx + 1, reply_markup)
    else:
        await show_final_result(update, feedback, quiz_state["score"], len(questions))
        context.user_data.pop("quiz", None)
