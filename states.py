"""
Defines the states for the Finite State Machine (FSM) used in the bot.

This module contains state groups that help manage the user's conversation flow,
for example, when a user is in the process of a quiz.
"""


from aiogram.fsm.state import State, StatesGroup

class QuizState(StatesGroup):
    """
    A StatesGroup that holds the states for the quiz process.
    """

    # This state indicates that the user is currently answering quiz questions.
    # We will store the user's score and progress in the data of this state.
    in_progress = State()

