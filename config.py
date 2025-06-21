# config.py
"""
Configuration file.
Contains bot settings and paths to data files.
"""
import os
from dotenv import load_dotenv

load_dotenv() # Loading environment variable from .env file

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if BOT_TOKEN is None:
    raise ValueError("Bot token not found in environment variables")

# Here are paths to files ↓
DEFINITIONS_PATH = "data/definitions.json"
QUIZ_QUESTIONS_PATH = "data/questions.json"
FACTS_PATH = "data/facts.json"