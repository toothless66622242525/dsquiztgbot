# handlers.py

"""
This module contains command handlers for a Telegram bot itself built with aiogram.

Features:
- /start: Greets the user and shows available commands
- /help: Shows help information for user
- /define <термин>: Looks up and returns the definition of a term from a definitions database
- /fact: Sends a random interesting fact from a database

The module loads definitions and facts from JSON files and handles errors gracefully if files are missing or corrupted.

All handlers are registered on a Router instance for later inclusion in the Dispatcher in main.py
"""

import json  # For work with JSON
import random  # For /fact command
from aiogram import Router, F  # F импортируем на будущее для фильтров по тексту/данным
from aiogram.filters import CommandStart, Command, CommandObject  # CommandObject на будущее для /define
from aiogram.types import Message, CallbackQuery  # CallbackQuery на будущее для квиза
from aiogram.utils.markdown import hbold  # Для выделения текста жирным
from aiogram.fsm.context import FSMContext
from states import QuizState

from keyboards import create_quiz_keyboard, get_next_quiz_keyboard

from config import DEFINITIONS_PATH, QUIZ_QUESTIONS_PATH, FACTS_PATH  # Importing paths from config.py

# Создаем экземпляр Router. Все обработчики будут регистрироваться на нем.
router = Router()

# --- Data loading ---
definitions_data = {}
facts_data = []
normalized_definitions_data = {}
quiz_questions_data = []

try:
    with open(DEFINITIONS_PATH, "r", encoding="UTF-8") as f:
        definitions_data = json.load(f)
        # Creating a "normalized" dictionary with definitions
        normalized_definitions_data = {key.lower(): (key, value) for key, value in definitions_data.items()}

except FileNotFoundError:
    definitions_data = {}
    print(f"WARNING! Файл {DEFINITIONS_PATH} не найден. Определения не будут доступны.")

except json.JSONDecodeError:
    definitions_data = {}
    print(f"WARNING! Ошибка декодирования JSON в файле {DEFINITIONS_PATH}.")

try:
    with open(FACTS_PATH, "r", encoding="UTF-8") as f:
        facts_data = json.load(f)

except FileNotFoundError:
    facts_data = []
    print(f"WARNING! Файл {FACTS_PATH} не найден. Факты не будут доступны.")

except json.JSONDecodeError:
    facts_data = []
    print(f"WARNING! Ошибка декодирования JSON в файле {FACTS_PATH}.")

try:
    with open(QUIZ_QUESTIONS_PATH, "r", encoding="UTF-8") as f:
        quiz_questions_data = json.load(f)

except FileNotFoundError:
    quiz_questions_data = []
    print(f"WARNING! Файл {QUIZ_QUESTIONS_PATH} не найден. Вопросы не будут доступны.")

except json.JSONDecodeError:
    quiz_questions_data = []
    print(f"WARNING! Ошибка декодирования JSON в файле {QUIZ_QUESTIONS_PATH}.")


# --- Обработчик команды /start ---
@router.message(CommandStart())  # Декоратор, регистрирующий функцию как обработчик команды /start
async def cmd_start(message: Message):  # Функция-обработчик, всегда async
    # Формируем текст ответа. Используем f-строку для удобной вставки имени пользователя.
    # Экранируем < и > as a lt; and gt; because of ParseMode.HTML
    text = (
        f" Привет, {hbold(message.from_user.full_name)}!\n"  # Using hbold to make the name bold
        f"Я твой помощник в мире Data Science. 🤖\n\n"
        f"Используй команды:\n"
        f"/define &lt;термин&gt; - узнать определение термина\n"
        f"/quiz - пройти небольшой квиз\n"
        f"/fact - получить интересный факт\n"
        f"/help - показать это сообщение еще раз\n"
    )
    # Sending a reply message to the user.
    await message.answer(text)


# --- The handler of the command /help ---
@router.message(Command("help"))  # A decorator that registers a function below as a handler for the /help
async def cmd_help(message: Message):  # Making handler for /help
    text = (
        f"Я твой помощник в мире Data Science. 🤖\n\n"
        f"Используй команды:\n"
        f"/define &lt;термин&gt; - узнать определение термина\n"
        f"/quiz - пройти небольшой квиз\n"
        f"/fact - получить интересный факт\n"
        f"/help - показать это сообщение еще раз\n"
    )
    # Sending a reply message to the user.
    await message.answer(text)


# --- The handler of the command /define ---
@router.message(Command("define"))  # A decorator that registers a function below as a handler for the /define
async def cmd_define(message: Message,
                     command: CommandObject):  # command: CommandObject - contains command arguments, like "Machine Learning, Big Data" and other definitions arguments in definitions.py
    if not definitions_data:
        await message.answer("Извините, база определений в данный момент недоступна.")
        return

    if command.args is None:
        await message.answer(
            'Looks like вы написали просто "/define"! Пожалуйста, укажите термин после /define.\n'
            'Например: /define Big Data'
        )
        return

    normalized_term = command.args.strip().lower()  # Normalizing entered term
    if normalized_term in normalized_definitions_data:
        original_term, definition = normalized_definitions_data[normalized_term]
        await message.answer(f"{hbold(original_term)}:\n{definition}")
    else:
        available_terms = ", ".join(definitions_data.keys())
        await message.answer(
            f"Термин '{command.args.strip()}' не найден.\n"  # Показываем пользователю то, что он ввел
            f"Попробуйте один из следующих терминов (регистр не важен): {hbold(available_terms)}"
        )


# --- The handler of the command /fact ---
@router.message(Command("fact"))
async def cmd_fact(message: Message):
    if not facts_data:
        await message.answer("Извините, база фактов в данный момент недоступна.")
        return

    random_fact = random.choice(facts_data)
    await message.answer(f"💡 {hbold('Интересный факт:')}\n{random_fact}")


async def send_quiz_question(source: Message | CallbackQuery):
    """
    Selects a random question, creates a keyboard for it, and sends it to the user.

    This function is universal and can handle two scenarios:
    1. Sending a new message (when triggered by a command like /quiz).
    2. Editing an existing message (when triggered by a callback, e.g., "Next question" button).

    :param source: The source of the trigger. Can be a 'Message' object or a 'CallbackQuery' object.
    """

    # --- BLOCK 1: Guard Clause - Check if there are any questions available ---
    # This is a safety check to prevent errors if the questions file is empty or wasn't loaded.
    if not quiz_questions_data:
        text = "Извините, вопросы для квиза закончились или не загружены."

        # Determine how to send the error message based on the source type.
        if isinstance(source, Message):
            await source.answer(text, reply_markup=None)
        # Edit the original message to show the error and remove the old keyboard.
        elif isinstance(source, CallbackQuery):
            await source.message.edit_text(text, reply_markup=None)
        # Log an error if an unexpected source type is received.
        else:
            print(f"Функция send_quiz_question получила неизвестный тип источника: {type(source)}")
        return

    # --- BLOCK 2: Select a question and get its data ---
    # This code only runs if the check in BLOCK 1 was passed.

    # Select one random question dictionary from the list.
    question_item = random.choice(quiz_questions_data)
    # Get the index of the chosen question. This will serve as its unique ID.
    question_id = quiz_questions_data.index(question_item)

    # Forming message's text
    text = f"Вопрос:\n{hbold(question_item['question'])}"

    # Create the keyboard for this specific question using our generator function.
    # We pass the list of options (from the 'options' key) and the unique question_id.
    keyboard = create_quiz_keyboard(question_item['options'], question_id)

    # --- BLOCK 4: Send or Edit the message ---
    # Check the source type again to decide on the action.

    # If the trigger was a command, send a new message with the question
    if isinstance(source, Message):
        await source.answer(text, reply_markup=keyboard)
    # If the trigger was a button press, edit the existing message to show em the new question.
    elif isinstance(source, CallbackQuery):
        await source.message.edit_text(text, reply_markup=keyboard)


# --- The handler of the command /quiz ---
@router.message(Command("quiz"))
async def cmd_quiz(message: Message, state: FSMContext):
    """
    Starts the quiz for the user.

    This handler sets the user's state to 'in_progress',
    resets their quiz score, and sends the first question.

    :param message: The message object from Telegram.
    :param state: The FSM context object for managing state.
    """

    # Set the user's state to QuizState.in_progress
    await state.set_state(QuizState.in_progress)
    # Store initial data for the quiz session (counters)
    await state.update_data(
        questions_answered=0,
        correct_answers=0
    )
    # Send the first question to the user
    await send_quiz_question(message)


# --- Handler for the "Next question" button ---
@router.callback_query(F.data == "quiz_next", QuizState.in_progress)
async def handle_next_quiz_question(callback: CallbackQuery):
    """
    Handles the "Next question" button in the quiz: sends a new random quiz question to the user, again, using send_quiz_question function.
    Then confirming accept of the callback
    """
    await send_quiz_question(callback)
    await callback.answer(text="Ваш ответ принят!")


# --- Handler for quiz answers ---
@router.callback_query(F.data.startswith("quizans_"), QuizState.in_progress)
async def handle_quiz_answer(callback: CallbackQuery, state: FSMContext):
    """
    Handles the user's answer to a quiz question, updates the score,
    and shows the result.

    This function is triggered when a user presses an answer button. It performs
    the following steps:
    1. Parses the callback data to identify the question and the chosen answer.
    2. Retrieves the user's current score from the FSM context.
    3. Checks if the answer is correct and updates the score.
    4. Saves the new score back to the FSM context.
    5. Edits the message to show the result and provides new action buttons.

    :param callback: The CallbackQuery object from the button press.
    :param state: The FSMContext object for managing the user's state and data.
    """

    # Step 1: Parse the callback_data to get the question ID and chosen answer index.
    # The format is "quizans_{question_id}_{chosen_option_index}".
    _, question_id_str, chosen_option_idx_str = callback.data.split("_")

    # Retrieve data from the state storage
    user_data = await state.get_data()
    q_answered = user_data.get('questions_answered', 0)
    c_answers = user_data.get('correct_answers', 0)

    # Convert string data to integers for further use.
    question_id = int(question_id_str)
    chosen_option_idx = int(chosen_option_idx_str)

    # Step 2: Retrieve the question data from our list using the question_id.
    question = quiz_questions_data[question_id]
    correct_option_idx = question["correct_option_index"]

    # Step 3: Check if the user's answer is correct and form the result text.
    if correct_option_idx == chosen_option_idx:
        result_text = f"✅ Правильно!\n\n"
        c_answers += 1
    # Get the text of the correct answer to show it to the user.
    else:
        correct_option_text = question['options'][correct_option_idx]
        result_text = f"❌ Неправильно. Правильный ответ: {hbold(correct_option_text)}\n\n"
    # Add an explanation to the result text if it exists and not empty for this question.

    q_answered += 1

    if "explanation" in question and question["explanation"]:
        result_text += f"💡 {hbold('Пояснение:')} {question['explanation']}"

    # Save the updated score back to the state
    await state.update_data(
        questions_answered=q_answered,
        correct_answers=c_answers
    )

    # Step 4: Edit the original message to show the question, result, and the "Next question" button.
    await callback.message.edit_text(text=f"{hbold('Вопрос:')}\n{question['question']}\n\n{result_text}",
                                     reply_markup=get_next_quiz_keyboard())

    # Step 5: Acknowledge the callback.
    await callback.answer(text="Cледующий вопрос!")


# --- Handler for finishing the quiz ---
@router.callback_query(F.data == "quiz_stop", QuizState.in_progress)
async def handle_quiz_finish(callback: CallbackQuery, state: FSMContext):
    """
    Handles the "Finish quiz" button press.

    This function calculates the user's final score, sends a summary message,
    and clears the user's state, effectively ending the quiz session.

    :param callback: The CallbackQuery object from the button press.
    :param state: The FSMContext object for managing the user's state.
    """
    # Retrieve the final score from the state storage.
    user_data = await state.get_data()
    questions_answered = user_data.get('questions_answered', 0)
    correct_answers = user_data.get('correct_answers', 0)

    # Calculate incorrect answers.
    wrong_answers = questions_answered - correct_answers

    # Form the final statistics message.
    stats_text = (
        f"🏁 Квиз завершен! 🏁\n\n"
        f"Ваш результат:\n"
        f"Отвечено вопросов: {hbold(questions_answered)}\n"
        f"✅ Правильных ответов: {hbold(correct_answers)}\n"
        f"❌ Неправильных ответов: {hbold(wrong_answers)}\n\n"
        f"Чтобы начать заново, просто введите /quiz"
    )

    # Edit the message to show the final stats and remove the keyboard.
    await callback.message.edit_text(text=stats_text, reply_markup=None)

    # Clear the user's state to exit the quiz mode.
    await state.clear()

    # Acknowledge the callback to stop the "loading" animation.
    await callback.answer()
