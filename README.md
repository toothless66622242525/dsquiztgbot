Data Science Quiz Bot 🤖

A sophisticated and interactive Telegram bot designed to help users learn and test their knowledge in the world of Data Science. Built with Python and the powerful `aiogram` 3 library.

✨ Features

- Interactive Quiz: Start a quiz with `/quiz` featuring multiple-choice questions on various Data Science topics.
- Scoring System: The bot tracks your score during a quiz session using a Finite State Machine (FSM) and shows your stats when you finish.
- Knowledge Base: Use the `/define <term>` command to get clear and concise definitions of common Data Science terms.
- Facts: Get a random interesting fact about data, machine learning, or statistics with the `/fact` command.
- State-of-the-art UX: Smoothly edits messages for a seamless quiz experience without spamming the chat.

🛠️ Technologies Used

- Language: Python 3.10+
- Telegram Bot Framework: [aiogram 3](https://github.com/aiogram/aiogram)
- State Management: Aiogram's Finite State Machine (FSM) for handling quiz sessions.
- Configuration: `python-dotenv` for secure management of environment variables.

🚀 Setup and Installation

Follow these steps to get the bot running locally.

1. Clone the repository
```bash
git clone https://github.com/toothless66622242525/dsquizbot.git
cd dsquizbot

2. Create and activate a virtual environment
This is a recommended practice to keep project dependencies isolated.

For Windows:
python -m venv .venv
.venv\Scripts\activate

For macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

3. Install dependencies
All required packages are listed in requirements.txt. Install them with a single command:

pip install -r requirements.txt

4. Configure the environment
You need to provide your Telegram Bot API token.

Create a file named .env in the root directory of the project.

Add your bot token to this file in the following format:

TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
Note: The .env file is listed in .gitignore and will not be committed to the repository for security reasons.

▶️ How to Run
Once the setup is complete, you can run the bot with this command:

python main.py

The bot will start polling for updates. You can now interact with it on Telegram!

📂 Project Structure
├── data/
│   ├── definitions.json
│   ├── facts.json
│   └── questions.json
├── .env (Must be created locally)
├── .gitignore
├── config.py
├── handlers.py
├── keyboards.py
├── main.py
├── requirements.txt
└── states.py
