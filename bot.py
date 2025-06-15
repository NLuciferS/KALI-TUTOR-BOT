import json
import logging
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# Put your Telegram bot token here (keep it secret!)
TOKEN = "8124805095:AAHpMKmdGzsZdHY1aw-TrfctMEQO7WaslAk"

# Enable logging for debugging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load Kali tools and commands from tools.json
with open("tools.json", "r", encoding="utf-8") as f:
    tools_data = json.load(f)

# State storage for quizzes (in-memory)
user_states = {}

# Constants
ITEMS_PER_PAGE = 5

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send main menu."""
    keyboard = [
        [InlineKeyboardButton("Learn Kali Tools", callback_data="learn_tools_0")],
        [InlineKeyboardButton("Practice Challenges", callback_data="practice")],
        [InlineKeyboardButton("Quiz Yourself", callback_data="quiz_start")],
        [InlineKeyboardButton("Red Team Roadmap", callback_data="roadmap")],
        [InlineKeyboardButton("Career Tips", callback_data="career")],
        [InlineKeyboardButton("Useful Resources", callback_data="resources")],
    ]

    text = "Welcome to Kali Tutor Bot! Choose an option:"

    if update.callback_query:
        await update.callback_query.edit_message_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        # It's good to answer the callback to remove the "loading" animation
        await update.callback_query.answer()
    else:
        await update.message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_tools(update: Update, context: ContextTypes.DEFAULT_TYPE, page: int):
    """Show Kali tools categories with pagination."""
    categories = list(tools_data.keys())
    start_index = page * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    keyboard = []

    for category in categories[start_index:end_index]:
        keyboard.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"learn_tools_{page-1}"))
    if end_index < len(categories):
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"learn_tools_{page+1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="start")])

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Select a category to learn Kali tools:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "Select a category to learn Kali tools:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_tools_in_category(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str):
    """Show tools in a chosen category."""
    tools = tools_data.get(category, [])
    if not tools:
        await update.callback_query.answer(text="No tools found in this category.", show_alert=True)
        return

    keyboard = []
    for tool in tools:
        keyboard.append([InlineKeyboardButton(tool['name'], callback_data=f"tool_{category}_{tool['name']}")])

    keyboard.append([InlineKeyboardButton("Back to Categories", callback_data="learn_tools_0")])
    keyboard.append([InlineKeyboardButton("Back to Main Menu", callback_data="start")])

    await update.callback_query.edit_message_text(
        f"Tools in category *{category}*:", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def show_tool_details(update: Update, context: ContextTypes.DEFAULT_TYPE, category: str, tool_name: str):
    """Show details and commands for a specific Kali tool."""
    tools = tools_data.get(category, [])
    tool = next((t for t in tools if t['name'] == tool_name), None)

    if not tool:
        await update.callback_query.answer(text="Tool not found.", show_alert=True)
        return

    msg = f"*{tool['name']}*\n_{tool.get('description', 'No description available.')}_\n\n"
    msg += "*Basic command:*\n"
    msg += f"`{tool.get('basic', 'N/A')}`\n\n"
    msg += "*Intermediate command:*\n"
    msg += f"`{tool.get('intermediate', 'N/A')}`"

    keyboard = [
        [InlineKeyboardButton("Back to Tools", callback_data=f"category_{category}")],
        [InlineKeyboardButton("Back to Main Menu", callback_data="main_menu")],
    ]

    await update.callback_query.edit_message_text(
        msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
    )

async def show_practice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show practice challenges placeholder."""
    text = (
        "Practice challenges will be added soon!\n"
        "Meanwhile, you can try labs on sites like Hack The Box or TryHackMe."
    )
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="start")]]
    await update.callback_query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_roadmap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show a brief Red Team roadmap."""
    roadmap_text = (
        "Red Team Roadmap Highlights:\n"
        "- Linux & Command Line Mastery\n"
        "- Network & Protocol Analysis\n"
        "- Exploitation Techniques\n"
        "- Privilege Escalation\n"
        "- Persistence & Post Exploitation\n"
        "- AV Evasion\n"
        "- C2 Frameworks\n"
        "For detailed roadmap, visit https://redteamroadmap.com/"
    )
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="start")]]
    await update.callback_query.edit_message_text(
        roadmap_text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_career(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show career tips."""
    career_text = (
        "Cybersecurity Career Tips:\n"
        "- Build strong fundamentals\n"
        "- Get hands-on practice\n"
        "- Participate in CTFs and bug bounties\n"
        "- Network with professionals\n"
        "- Keep learning and updating skills\n"
        "- Prepare for certifications like OSCP"
    )
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="start")]]
    await update.callback_query.edit_message_text(
        career_text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def show_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show useful resources."""
    resources_text = (
        "Useful Kali Linux Resources:\n"
        "- Official Kali Docs: https://www.kali.org/docs/\n"
        "- Offensive Security Training: https://www.offensive-security.com/\n"
        "- TryHackMe: https://tryhackme.com/\n"
        "- Hack The Box: https://www.hackthebox.eu/\n"
        "- OverTheWire Wargames: https://overthewire.org/wargames/"
    )
    keyboard = [[InlineKeyboardButton("Back to Main Menu", callback_data="start")]]
    await update.callback_query.edit_message_text(
        resources_text, reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Quiz questions example
quiz_questions = [
    {
        "question": "Which tool is used for network scanning?",
        "options": ["nmap", "hydra", "john"],
        "answer": "nmap",
    },
    {
        "question": "Which tool is used for password cracking?",
        "options": ["john", "nmap", "netcat"],
        "answer": "john",
    },
    # Add more questions if you want
]

async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    user_states[user_id] = {"quiz_index": 0, "score": 0}
    await send_quiz_question(update, context)

async def send_quiz_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    state = user_states.get(user_id)
    if not state:
        return
    index = state["quiz_index"]
    if index >= len(quiz_questions):
        await update.callback_query.edit_message_text(
            f"Quiz complete! Your score: {state['score']}/{len(quiz_questions)}\n"
            "Use /start to play again."
        )
        user_states.pop(user_id)
        return

    q = quiz_questions[index]
    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"quiz_answer_{opt}")] for opt in q["options"]
    ]
    buttons.append([InlineKeyboardButton("Quit Quiz", callback_data="start")])

    await update.callback_query.edit_message_text(
        q["question"], reply_markup=InlineKeyboardMarkup(buttons)
    )

async def handle_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    state = user_states.get(user_id)
    if not state:
        await update.callback_query.answer("No active quiz found. Use /start to begin.")
        return

    selected = update.callback_query.data.split("_")[-1]
    index = state["quiz_index"]
    correct = quiz_questions[index]["answer"]

    if selected == correct:
        state["score"] += 1
        reply = "Correct! ✅"
    else:
        reply = f"Wrong! ❌ The correct answer was: {correct}"

    state["quiz_index"] += 1
    await update.callback_query.answer(reply, show_alert=True)
    await send_quiz_question(update, context)

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "start":
        await start(update, context)

    elif data.startswith("learn_tools_"):
        page = int(data.split("_")[-1])
        await show_tools(update, context, page)

    elif data.startswith("category_"):
        category = data.split("_", 1)[1]
        await show_tools_in_category(update, context, category)

    elif data.startswith("tool_"):
        _, category, tool_name = data.split("_", 2)
        await show_tool_details(update, context, category, tool_name)

    elif data == "practice":
        await show_practice(update, context)

    elif data == "quiz_start":
        await start_quiz(update, context)

    elif data.startswith("quiz_answer_"):
        await handle_quiz_answer(update, context)

    elif data == "roadmap":
        await show_roadmap(update, context)

    elif data == "career":
        await show_career(update, context)

    elif data == "resources":
        await show_resources(update, context)

    else:
        await query.answer("Unknown command!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
