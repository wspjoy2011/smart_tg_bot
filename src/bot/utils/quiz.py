from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove

from db.repository import GptThreadRepository
from db.enums import MessageRole


def evaluate_answer(user_answer: str, correct_answer: str) -> tuple[str, bool]:
    """
    Compares the user's answer to the correct one and returns feedback.

    Args:
        user_answer (str): The answer provided by the user.
        correct_answer (str): The correct answer for the current quiz question.

    Returns:
        tuple[str, bool]: A tuple containing the feedback message (HTML-formatted) and a boolean
        indicating whether the answer was correct.
    """
    is_correct = user_answer.lower() == correct_answer.lower()
    feedback = "✅ Correct!" if is_correct else f"❌ Wrong! Correct: <b>{correct_answer}</b>"
    return feedback, is_correct


async def store_quiz_interaction(
        thread_repository: GptThreadRepository,
        thread_id: str,
        user_answer: str,
        feedback: str
) -> None:
    """
    Stores the user's quiz answer and assistant feedback in the database.

    Args:
        thread_repository (GptThreadRepository): Repository to interact with the SQLite database.
        thread_id (str): The OpenAI thread ID associated with the quiz session.
        user_answer (str): The answer selected by the user.
        feedback (str): The feedback message provided by the assistant.
    """
    await thread_repository.add_message(thread_id, MessageRole.USER.value, user_answer)
    await thread_repository.add_message(thread_id, MessageRole.ASSISTANT.value, feedback)


async def show_next_question(
        update: Update,
        feedback: str,
        question_data: dict,
        index: int,
        reply_markup: ReplyKeyboardMarkup
) -> None:
    """
    Sends the next quiz question to the user along with answer options.

    Args:
        update (telegram.Update): Telegram update containing user interaction.
        feedback (str): The feedback message from the previous answer.
        question_data (dict): The next question object containing 'question' and 'options'.
        index (int): The question number (1-based index) to display.
        reply_markup (ReplyKeyboardMarkup): The keyboard markup with answer options.
    """
    await update.message.reply_html(
        f"{feedback}\n\n<b>Question {index}:</b>\n{question_data['question']}",
        reply_markup=reply_markup
    )


async def show_final_result(
        update: Update,
        feedback: str,
        score: int,
        total: int
) -> None:
    """
    Displays the final score and quiz completion message to the user.

    Args:
        update (telegram.Update): Telegram update containing user interaction.
        feedback (str): The feedback message from the final answer.
        score (int): Total number of correct answers by the user.
        total (int): Total number of questions in the quiz.
    """
    await update.message.reply_html(
        f"{feedback}\n\n🎉 <b>Quiz Complete!</b>\nYour Score: <b>{score}/{total}</b>",
        reply_markup=ReplyKeyboardRemove()
    )
