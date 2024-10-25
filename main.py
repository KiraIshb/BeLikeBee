import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.constants import ParseMode

# Создаем базу данных и таблицу
def init_db():
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task NVARCHAR(25) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Инициализируем базу данных
def init_db():
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Функция для добавления задачи
def add_task(user_id: int, task: str):
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (user_id, task))
    conn.commit()
    conn.close()


# Функция для удаления задачи
def delete_task(user_id: int, task_id: int):
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id))
    conn.commit()
    conn.close()


#Функция для того чтобы отметить задачу выполненной
def complite_task(user_id: int, task_id: int):
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    #task = cursor.execute('SELECT task FROM tasks WHERE user_id = ? AND id = ?', (user_id, task_id))
    cursor.execute("UPDATE tasks SET task = CONCAT('<s>', task, '</s>') WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

#Функция для того чтобы отметить задачу приоритетной
def priority_task(user_id: int, task_id: int):
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    #task = cursor.execute('SELECT task FROM tasks WHERE user_id = ? AND id = ?', (user_id, task_id))
    cursor.execute("UPDATE tasks SET task = CONCAT(task, '❗️') WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

# Функция для отображения всех задач
def show_tasks(user_id: int) -> str:
    conn = sqlite3.connect('telegram_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, task FROM tasks WHERE user_id = ?', (user_id,))
    tasks = cursor.fetchall()
    conn.close()
    if not tasks:
        return "У вас нет задач."

    response = "А вот и список дел:\n"
    for task in tasks:
        response += f"• {task[1]} (id: {task[0]})\n"
    return response


# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Добро пожаловать в ряды правильных пчёлок 🐝\nДля открытия меню команд жми /command")

# Обработчик команды /command
async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Вот, что я умею:"+
                                    "\n/add &lt задача &gt - добавит задачу в список дел"+
                                    "\n/delete &lt id &gt - удалит задачу по этому id (каждой задаче присваивается уникальный id, узнать его можно из списка дел)"+
                                    "\n/tasks - выведет список дел"+
                                    "\n/complite - отметит задачу выполненной"+
                                    "\n/priority &lt id &gt - для самых важных задач"+
                                    "\n<em>Планы - ничто, планирование - всё! *бззз*</em>", parse_mode='HTML')

# Обработчик команды /add
async def add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    task = ' '.join(context.args)
    if task:
        add_task(user_id, task)
        await update.message.reply_text("<em>Отлично!</em>"+
                                        f"\nЗадача {task} добавлена в список дел 👍", parse_mode='HTML')
    else:
        await update.message.reply_text("Пожалуйста, укажите задачу для добавления.")


# Обработчик команды /delete
async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.args:
        try:
            task_id = int(context.args[0])
            delete_task(user_id, task_id)
            await update.message.reply_text(f"<em>Правильным пчёлам - правильный мёд!</em>\nЗадача {task_id} удалена 🗑", parse_mode='HTML')
        except ValueError:
            await update.message.reply_text("Пожалуйста, укажите правильный ID задачи для удаления.")
    else:
        await update.message.reply_text("Пожалуйста, укажите ID задачи для удаления.")

# Обработчик команды /complite
async def complite(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.args:
        try:
            task_id = int(context.args[0])
            complite_task(user_id, task_id)
            await update.message.reply_text(f"<em>Ура!</em>\nЗадача {task_id} выполнена ✅", parse_mode='HTML')
        except ValueError:
            await update.message.reply_text("Пожалуйста, укажите правильный ID задачи для выполнения.")
    else:
        await update.message.reply_text("Пожалуйста, укажите ID задачи для выполнения.")

# Обработчик команды /priority
async def priority(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if context.args:
        try:
            task_id = int(context.args[0])
            priority_task(user_id, task_id)
            await update.message.reply_text(f"<em>*бззз*</em>\nЗадача {task_id} отмечена важной ☀️", parse_mode='HTML')
        except ValueError:
            await update.message.reply_text("Пожалуйста, укажите правильный ID задачи для priority.")
    else:
        await update.message.reply_text("Пожалуйста, укажите ID задачи для priority.")


# Обработчик команды /tasks
async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    tasks_list = show_tasks(user_id)
    await update.message.reply_text(tasks_list, parse_mode="HTML")


# Основная функция запуска бота
if __name__ == '__main__':
    init_db()  # Инициализируем базу данных
    application = ApplicationBuilder().token('7831089520:AAHQZ5KvQYibTQMv7OUUAJwDe_Xmie3bHrw').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("command", command))
    application.add_handler(CommandHandler("add", add))
    application.add_handler(CommandHandler("delete", delete))
    application.add_handler(CommandHandler("complite", complite))
    application.add_handler(CommandHandler("priority", priority))
    application.add_handler(CommandHandler("tasks", tasks))

    application.run_polling()