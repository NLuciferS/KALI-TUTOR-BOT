from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
import logging

# Enable logging for easier debugging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Your Telegram bot token here (replace with your actual token)
TOKEN = "8124805095:AAHpMKmdGzsZdHY1aw-TrfctMEQO7WaslAk"

# Sample data for Kali tools explanations
TOOLS_INFO = {
    "nmap": "Nmap (Network Mapper) is a powerful open source tool used for network discovery and security auditing.",
    "netcat": "Netcat (nc) is a versatile networking tool used for reading/writing across network connections using TCP or UDP.",
    "hydra": "Hydra is a fast and flexible login cracker which supports many protocols to perform brute force attacks."
}

# Quiz questions and answers
QUIZ_QUESTIONS = [
    {
        "question": "What command is used for network scanning in Kali Linux?",
        "options": ["hydra", "nmap", "netcat", "john"],
        "answer": "nmap"
    },
    {
        "question": "Which tool is used for brute forcing passwords?",
        "options": ["hydra", "nmap", "tcpdump", "wireshark"],
        "answer": "hydra"
    },
    {
        "question": "Netcat is primarily used for?",
        "options": ["Password cracking", "Network scanning", "Reading/writing network connections", "Packet sniffing"],
        "answer": "Reading/writing network connections"
    }
]

# To keep track of quiz states per user (simple in-memory, lost on restart)
user_quiz_states = {}

# Start command handler - main menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Learn a Tool 🔧", callback_data='learn_tool')],
        [InlineKeyboardButton("Daily Practice 💪", callback_data='daily_practice')],
        [InlineKeyboardButton("Ask a Command 🧠", callback_data='ask_command')],
        [InlineKeyboardButton("Kali Quiz 🎮", callback_data='kali_quiz')],
        [InlineKeyboardButton("Career Tips 👨‍💻", callback_data='career_tips')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Welcome to Kali Tutor Bot! Choose an option:",
        reply_markup=reply_markup
    )

# Handle button clicks from inline keyboard
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == 'learn_tool':
        # Show list of tools to choose from
        keyboard = [
            [InlineKeyboardButton("nmap", callback_data='tool_nmap')],
            [InlineKeyboardButton("netcat", callback_data='tool_netcat')],
            [InlineKeyboardButton("hydra", callback_data='tool_hydra')],
            [InlineKeyboardButton("Back to Main Menu", callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Choose a Kali tool to learn about:",
            reply_markup=reply_markup
        )

    elif data.startswith('tool_'):
        tool_name = data.split('_')[1]
        info = TOOLS_INFO.get(tool_name, "Sorry, no info available for this tool yet.")
        await query.edit_message_text(
            text=f"**{tool_name.upper()}**\n\n{info}\n\nType /start to return to main menu.",
            parse_mode='Markdown'
        )

    elif data == 'daily_practice':
        await query.edit_message_text(
            text="Today's practice:\nUse this Nmap command to scan a target:\n\n`nmap -sS <target-ip>`\n\nTry it and let me know if you have questions!"
            , parse_mode='Markdown'
        )

    elif data == 'ask_command':
        await query.edit_message_text(
            text="Send me a Kali command (e.g., nmap, netcat), and I'll explain it."
        )

    elif data == 'kali_quiz':
        # Start quiz for the user
        user_id = query.from_user.id
        user_quiz_states[user_id] = {
            "score": 0,
            "current_q": 0
        }
        await send_quiz_question(user_id, query, context)

    elif data == 'career_tips':
        tips = (
            "🛠️ Stay updated with cybersecurity news.\n"
            "💻 Practice daily on tools like Nmap and Netcat.\n"
            "📚 Read blogs and watch tutorials.\n"
            "🔐 Join cybersecurity communities.\n"
            "🎯 Build your own labs and practice attacks safely."
        )
        await query.edit_message_text(tips)

    elif data == 'main_menu':
        # Go back to main menu
        await start(update, context)

    elif data.startswith('quiz_answer_'):
        user_id = query.from_user.id
        selected_answer = data.split('_', 2)[2]

        if user_id not in user_quiz_states:
            await query.edit_message_text("Please start the quiz first by selecting Kali Quiz 🎮 from the menu.")
            return

        state = user_quiz_states[user_id]
        current_q = state["current_q"]
        correct_answer = QUIZ_QUESTIONS[current_q]["answer"]

        if selected_answer == correct_answer:
            state["score"] += 1
            reply = "✅ Correct!"
        else:
            reply = f"❌ Wrong! The correct answer was: {correct_answer}"

        # Move to next question
        state["current_q"] += 1

        if state["current_q"] < len(QUIZ_QUESTIONS):
            await query.edit_message_text(reply)
            await send_quiz_question(user_id, query, context)
        else:
            final_score = state["score"]
            total = len(QUIZ_QUESTIONS)
            await query.edit_message_text(f"{reply}\n\nQuiz complete! Your final score: {final_score}/{total}\n\nType /start to play again.")
            del user_quiz_states[user_id]

async def send_quiz_question(user_id, query, context):
    state = user_quiz_states[user_id]
    current_q = state["current_q"]
    question_data = QUIZ_QUESTIONS[current_q]

    # Build inline keyboard for options
    keyboard = []
    for option in question_data["options"]:
        callback_data = f"quiz_answer_{option}"
        keyboard.append([InlineKeyboardButton(option, callback_data=callback_data)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(question_data["question"], reply_markup=reply_markup)

# Handle free text messages from user (like ask_command feature)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.lower()

    # Basic command explanations
    if "nmap" in user_text:
        response = TOOLS_INFO["nmap"]
    elif "netcat" in user_text or "nc" in user_text:
        response = TOOLS_INFO["netcat"]
    elif "hydra" in user_text:
        response = TOOLS_INFO["hydra"]
    else:
        response = "Sorry, I can only explain basic Kali Linux tools for now. Try asking about nmap, netcat, or hydra."

    await update.message.reply_text(response)

# Error handler to catch unexpected errors
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    if update and hasattr(update, "message") and update.message:
        await update.message.reply_text("Oops! Something went wrong. Please try again later.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))  # same as start

    # Callback query handler for buttons
    app.add_handler(CallbackQueryHandler(button_handler))

    # Message handler for text messages (ask_command)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Error handler
    app.add_error_handler(error_handler)

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
