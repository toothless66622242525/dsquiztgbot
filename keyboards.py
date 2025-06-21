# keyboards.py
"""
A module for creating inline keyboards for a Telegram bot.

This module contains generator functions for creating various
types of keyboards used in the bot, exactly for a quiz itself.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def create_quiz_keyboard(options: List[str], question_id: int) -> InlineKeyboardMarkup:
    """
    Creates an inline keyboard for a quiz question.

    :param options: A list of strings with answer options.
    :param question_id: The question ID to identify which question is being answered.
    :return: An InlineKeyboardMarkup object.
    """

    buttons = []  # Initializing the list for buttons

    # Start of a cycle for sorting through possible answers
    for i, option_text in enumerate(options):
        # Forming the callback_data in the format "prefix_id-question_index-response".
        # This will allow us to easily determine in the handler which question and which option the user answered.
        callback_data = f"quizans_{question_id}_{i}"

        # Creating a button object and attaching text on the button and callback_data
        button = InlineKeyboardButton(
            text=option_text,
            callback_data=callback_data
        )

        # Adding a button to the list with all buttons
        buttons.append([button])

        # Creating and returning a keyboard object
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_next_quiz_keyboard() -> InlineKeyboardMarkup:
    """
    Creates and returns an inline keyboard with a "Next question" "Finish quiz" buttons.

        It is used after the user has answered the question,
        to invite him to move on to the next one or finish the quiz and get their stats.

        :return: An InlineKeyboardMarkup object with one button.
        """
    buttons = [
        [
            InlineKeyboardButton(text="Следующий вопрос 🤔", callback_data="quiz_next")
        ],
        [
            InlineKeyboardButton(text="Закончить квиз 🏁", callback_data="quiz_stop")
        ]
    ]
    # Creating and returning a keyboard object
    return InlineKeyboardMarkup(inline_keyboard=buttons)
