from aiogram.types import *
import datetime, os
import linecache
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command, state
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder
import json, random
from aiogram.types import BotCommand

from db import create_db, add_user, get_all_user_ids

load_dotenv()

dp = Dispatcher()
bot = Bot(token=os.getenv('Token'))

END_FILE = "end_day.json"
NEW_FILE = "new_thought.json"
LIST_FILE = "lists.json"
TASK_FILE = "month_task.json"

class FormState(StatesGroup):
    list_stage = State()
    add_list_stage = State()
    finish_list_stage = State()
    num_list_stage = State()
    change_list_stage = State()
    main_goal = State()
    text = State()
    new_thought = State()
    name_text = State()
    question = State()
    add_month_purpose = State()
    finish_month_purpose = State()
    add_year_purpose = State()
    finish_year_purpose = State()
    add_problems = State()
    task_month = State()
    finish_problems = State()
    set_birthday = State()

def get_date_last_month(date):
  try:
    return date.replace(month=date.month - 1)
  except ValueError:
      if date.month == 1:
          last_day_of_december = datetime.date(date.year - 1, 12, 31)
          return last_day_of_december
      else:
          try:
            return date.replace(month=date.month-1, day=31)
          except ValueError:
            try:
                return date.replace(month=date.month - 1, day=30)
            except ValueError:
                return date.replace(month=date.month - 1, day=28)

def load_data(file):
    with open(file, 'r') as f:
        try:
            data = json.load(f)
        except:
            return {}
    return data

def save_data(file, data):
    with open(file, 'w') as file:
        json.dump(data, file, indent=4)

def show_problem(user_id):
    list_problems = load_data(LIST_FILE)
    if user_id in list_problems["list_problems"]:
        if len(list_problems["list_problems"][user_id]) != 0:
            list_problem = "Список твоих проблем, с которыми мы боремся:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_problems["list_problems"][user_id]))
            return list_problem
    return 0

def show_month(user_id):
    list_purpose_month = load_data(LIST_FILE)
    if user_id in list_purpose_month["list_purpose_month"]:
        if len(list_purpose_month["list_purpose_month"][user_id]) != 0:
            list_month = "Твои цели на этот месяц:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_purpose_month["list_purpose_month"][user_id]))
            return list_month
    return 0

def show_year(user_id):
    list_purpose_year = load_data(LIST_FILE)
    if user_id in list_purpose_year["list_purpose_year"]:
        if len(list_purpose_year["list_purpose_year"][user_id]) != 0:
            list_year = "Твои цели на этот год:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_purpose_year["list_purpose_year"][user_id]))
            return list_year
    return 0

async def set_commands():
    commands = [
        BotCommand(command="/info", description="Получить информацию обо мне и моих командах"),
        BotCommand(command="/actions", description="Возможные действия и функционал"),
        BotCommand(command="/list", description="Просмотр своих записей итогов дня"),
        BotCommand(command="/list_thought", description="Просмотр записей своих мыслей"),
        BotCommand(command="/change_main", description="Установка или изменение основной цели на день"),
        BotCommand(command="/task_month", description="Просмотр ежемесячных заданий"),
        BotCommand(command="/set_birthday", description="Установка даты рождения")
    ]
    await bot.set_my_commands(commands)

@dp.message(FormState.task_month)
async def task_month(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task_e = msg.text.strip()
    if task_e.lower() != "нет":
        tasks_mon = load_data(TASK_FILE)
        now = datetime.datetime.now().date()
        if user_id not in tasks_mon:
            tasks_mon[user_id] = {}
        tasks_mon[user_id][str(now)] = task_e
        save_data(TASK_FILE, tasks_mon)
        await state.clear()
        await msg.answer(f"Молодец, твоё задание сохранено!")
        if len(tasks_mon[user_id]) > 1:
            n = get_date_last_month(now)
            await msg.answer(f"Давай посмотрим на твой ответ месяц назад")
            await msg.answer(f"{tasks_mon[user_id][str(n)]}")
    else:
        await msg.answer(f"Хорошо, всё осталось прежним")

@dp.message(FormState.set_birthday)
async def set_birthday(msg: Message, state: FSMContext):
    await state.clear()
    user_id = str(msg.from_user.id)
    task = msg.text.strip()
    birthday = load_data(LIST_FILE)
    try:
        birt = datetime.datetime.strptime(task, "%d-%m-%Y")
        birthday["set_birthday"][user_id] = task
        save_data(LIST_FILE, birthday)
        await msg.answer(f"Дата установлена")
    except:
        await msg.answer(f"Введён неверный формат, дата не установлена")

@dp.message(FormState.question)
async def quest_task(msg: Message, state: FSMContext):
    await state.clear()
    decision = ["Бесспорно ты прав", "Увы, но нет", "Весьма вероятно", "Ответ положительный", "Перспективы не радужные", "Прогноз неблагоприятный", "Не обнадеживай себя", "Знаки говорят – да", "Не сейчас", "Маловероятно", "Ни в коем случае", "Не думаю", "Шансы невелики", "Определенно да", "Никогда", "Наверняка да", "Не вижу положительных знаков", "Кажется, что да", "Это судьба", "Похоже, что нет", "Скорее всего да", "Похоже на то", "Не гарантировано", "Вероятность высока", "Стоит попробовать", "Да, но будь осторожен", "Удача на твоей стороне", "Это исключено"]
    await msg.answer(f"{random.choice(decision)}")
    await msg.answer("Подумай о том, что ты почувствовал после моего ответа и поступай, как считаешь нужным")

@dp.message(FormState.add_problems)
async def process_add_problems(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task = msg.text.strip()
    list_problems = load_data(LIST_FILE)
    if user_id not in list_problems["list_problems"]:
        list_problems["list_problems"][user_id] = []
    list_problems["list_problems"][user_id].append(task)
    save_data(LIST_FILE, list_problems)
    await state.clear()
    await msg.answer(f"Проблема зафиксирована, теперь нам легче её решить")

@dp.message(FormState.finish_problems)
async def process_finish_problems(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    listed = load_data(LIST_FILE)
    await state.clear()
    try:
        task = int(msg.text)
        if 0 < task <= len(listed["list_problems"][user_id]):
            if listed["status"][user_id] == 1:
                if user_id not in listed["list_finish"]:
                    listed["list_finish"][user_id] = []
                listed["list_finish"][user_id].append(listed["list_problems"][user_id][task-1])
            listed["status"][user_id] = 0
            del listed["list_problems"][user_id][task-1]
            save_data(LIST_FILE, listed)
            await msg.answer('Готово')
        else:
            await msg.answer('Нет проблемы с таким номером, попробуй ещё раз')
    except:
        await msg.answer('Что-то пошло не так, необходимо было ввести число')

@dp.message(FormState.add_month_purpose)
async def process_add_purpose_month(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task = msg.text.strip()
    list_pur = load_data(LIST_FILE)
    if user_id not in list_pur["list_purpose_month"]:
        list_pur["list_purpose_month"][user_id] = []
    list_pur["list_purpose_month"][user_id].append(task)
    await state.clear()
    if user_id not in list_pur["list_date_month"]:
        list_pur["list_date_month"][user_id] = []
    future_date = datetime.datetime.now() + datetime.timedelta(days=30)
    formatted_date = future_date.strftime("%d-%m-%Y")
    list_pur["list_date_month"][user_id].append(formatted_date)
    save_data(LIST_FILE, list_pur)
    await msg.answer(f"Цель установлена, достигни ее за 30 дней, то есть до {formatted_date}")

@dp.message(FormState.finish_month_purpose)
async def process_finish_purpose_month(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    list_s = load_data(LIST_FILE)
    await state.clear()
    try:
        task = int(msg.text.strip())
        if 0 < task <= len(list_s["list_purpose_month"][user_id]):
            if list_s["status"][user_id] == 1:
                if user_id not in list_s["list_finish"]:
                    list_s["list_finish"][user_id] = []
                list_s["list_finish"][user_id].append(list_s["list_purpose_month"][user_id][task - 1])
            list_s["status"][user_id] = 0
            del list_s["list_purpose_month"][user_id][task - 1]
            del list_s["list_date_month"][user_id][task - 1]
            save_data(LIST_FILE, list_s)
            await msg.answer('Готово')
        else:
            await msg.answer('Нет цели с таким номером, попробуй ещё раз')
    except:
        await msg.answer('Что-то пошло не так, необходимо было ввести число')

@dp.message(FormState.add_year_purpose)
async def process_add_purpose_year(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task = msg.text.strip()
    list_purp = load_data(LIST_FILE)
    if user_id not in list_purp["list_purpose_year"]:
        list_purp["list_purpose_year"][user_id] = []
    list_purp["list_purpose_year"][user_id].append(task)
    await state.clear()
    if user_id not in list_purp["list_date_year"]:
        list_purp["list_date_year"][user_id] = []
    future_date = datetime.datetime.now() + datetime.timedelta(days=365)
    formatted_date = future_date.strftime("%d-%m-%Y")
    list_purp["list_date_year"][user_id].append(formatted_date)
    save_data(LIST_FILE, list_purp)
    await msg.answer(f"Цель установлена, достигни ее за 365 дней, то есть до {formatted_date}")

@dp.message(FormState.finish_year_purpose)
async def process_finish_purpose_year(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    list_pur = load_data(LIST_FILE)
    await state.clear()
    try:
        task = int(msg.text.strip())
        if 0 < task <= len(list_pur["list_purpose_year"][user_id]):
            if list_pur["status"][user_id] == 1:
                if user_id not in list_pur["list_finish"]:
                    list_pur["list_finish"][user_id] = []
                list_pur["list_finish"][user_id].append(list_pur["list_purpose_year"][user_id][task - 1])
            list_pur["status"][user_id] = 0
            del list_pur["list_purpose_year"][user_id][task - 1]
            del list_pur["list_date_year"][user_id][task - 1]
            save_data(LIST_FILE, list_pur)
            await msg.answer('Готово')
        else:
            await msg.answer('Нет цели с таким номером, попробуй ещё раз')
    except:
        await msg.answer('Что-то пошло не так, необходимо было ввести число')

# запись самочувствия в файл
@dp.message(FormState.text)
async def end_day_text(msg: Message, state: FSMContext):
    await state.clear()
    today = datetime.date.today()
    formatted_date = today.strftime("%d-%m-%Y")
    user_id = str(msg.from_user.id)
    text_1 = msg.text.strip()
    configuration = load_data(END_FILE)

    if user_id not in configuration:
        configuration[user_id] = {}
    configuration[user_id][formatted_date] = text_1

    save_data(END_FILE, configuration)
    await msg.answer("Запись сделана. Прочитать свои записи ты можешь в /list")
    await msg.answer("Не забывай, что ты молодец, потому что всё ещё работаешь здесь со мной!")

# запись мыслей в файл
@dp.message(FormState.new_thought)
async def new_thought(msg: Message, state: FSMContext):
    await state.clear()
    text = load_data(LIST_FILE)
    user_id = str(msg.from_user.id)
    text["text"][user_id] = msg.text.strip()
    save_data(LIST_FILE, text)
    await msg.answer("Как назовём эту заметку?")
    await state.set_state(FormState.name_text)

@dp.message(FormState.name_text)
async def name_text(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task_s = msg.text.strip()
    text = load_data(LIST_FILE)
    config = load_data(NEW_FILE)
    if user_id not in config:
        config[user_id] = {}
    else:
        if len(config[user_id].key()) != 0:
            for i in config[user_id]:
                if i == task_s:
                    await msg.answer("Запись с таким названием уже есть, придумай другую")
            await state.clear()

    config[user_id][task_s] = text["text"][user_id]
    save_data(NEW_FILE, config)
    await msg.answer("Запись сделана. Прочитать свои мысли ты можешь в /list_thought")

# составление списка дел
@dp.message(FormState.list_stage)
async def list_stage(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task_e = msg.text.strip()
    list_task = load_data(LIST_FILE)
    if task_e.lower() == "готово":
        await state.clear()
        if len(list_task["list_tasks"][user_id]) != 0:
            todo_list_text = "Ваш список дел:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_task["list_tasks"][user_id]))
            save_data(LIST_FILE, list_task)
            try:
                await bot.unpin_chat_message(chat_id=msg.chat.id)
            except:
                pass
            sent_message = await msg.answer(todo_list_text)
            await bot.pin_chat_message(chat_id=user_id, message_id=sent_message.message_id)
            await msg.answer("Давай теперь выберем самую важную цель на сегодня, на которой у нас будет фокус. Напиши номер этой задачи числом")
            await state.set_state(FormState.main_goal)
        else:
            await msg.answer("Ваш список дел пуст")
    else:
        list_task["list_tasks"][user_id].append(task_e)
        list_task["count_list"][user_id] += 1
        save_data(LIST_FILE, list_task)
        await msg.answer("Задача добавлена в список. Присылай ещё или напиши 'готово'")

@dp.message(FormState.main_goal)
async def process_main_goal(msg: Message, state: FSMContext):
    await state.clear()
    user_id = str(msg.from_user.id)
    list_tasks = load_data(LIST_FILE)
    try:
        task = int(msg.text.strip())
        try:
            if len(list_tasks["main_goal"][user_id]) == 0:
                list_tasks["count_list"][user_id] += 1
        except:pass
        if 0 < task <= len(list_tasks["list_tasks"][user_id]):
            list_tasks["main_goal"][user_id] = list_tasks["list_tasks"][user_id][task - 1]
            await msg.answer(f'Цель установлена. Не забудь обязательно выполнить: {list_tasks["main_goal"][user_id]}!')
        else:
            await msg.answer('Нет задачи с таким номером, попробуй ещё раз')
        save_data(LIST_FILE, list_tasks)
    except:
        await msg.answer('Что-то пошло не так, необходимо было ввести число')
        await msg.answer('Цель не установлена, установи ее в /change_main')

@dp.message(FormState.add_list_stage)
async def process_add_task(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    task2 = msg.text.strip()
    list_task = load_data(LIST_FILE)
    try:
        num = int(task2.split(",")[-1])
        if 0 < num <= len(list_task["list_tasks"][user_id]):
            list_task["list_tasks"][user_id].insert(num - 1, ','.join(task2.split(',')[:-1]))
        else:
            list_task["list_tasks"][user_id].insert(len(list_task["list_tasks"][user_id]), task2)
    except:
        num = len(list_task["list_tasks"][user_id])
        list_task["list_tasks"][user_id].insert(num, task2)

    list_task["count_list"][user_id] += 1
    await state.clear()
    save_data(LIST_FILE, list_task)
    todo_list_text = "Ваш список дел:\n" + "\n".join(f"{i + 1}. {task1}" for i, task1 in enumerate(list_task["list_tasks"][user_id]))
    try:
        await bot.unpin_chat_message(chat_id=msg.chat.id)
    except:
        pass
    sent_message = await msg.answer(todo_list_text)
    await bot.pin_chat_message(chat_id=user_id, message_id=sent_message.message_id)

@dp.message(FormState.finish_list_stage)
async def process_finish_task(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    list_task = load_data(LIST_FILE)
    try:
        number = int(msg.text.strip())
        if 0 < number <= len(list_task["list_tasks"][user_id]):
            if list_task["status"][user_id] == 1:
                list_task["count_task"][user_id] += 1
                if user_id not in list_task["list_great_tasks"]:
                    list_task["list_great_tasks"][user_id] = []
                list_task["list_great_tasks"][user_id].append(list_task["list_tasks"][user_id][number - 1])
            list_task["status"][user_id] = 0
            if list_task["list_tasks"][user_id][number - 1] == list_task["main_goal"][user_id]:
                list_task["count_task"][user_id] += 1
                await msg.answer('Ура! Цель выполнена, ты большой молодец!')
            del list_task["list_tasks"][user_id][number - 1]
        else:
            await msg.answer('Нет задачи с таким номером, попробуй ещё раз')
    except:
        await msg.answer('Что-то пошло не так, необходимо было ввести число')
    await state.clear()
    save_data(LIST_FILE, list_task)
    todo_list_text = "Ваш список дел:\n" + "\n".join(f"{i + 1}. {task1}" for i, task1 in enumerate(list_task["list_tasks"][user_id]))
    try:
        await bot.unpin_chat_message(chat_id=msg.chat.id)
    except:
        pass
    sent_message = await msg.answer(todo_list_text)
    await bot.pin_chat_message(chat_id=user_id, message_id=sent_message.message_id)

@dp.message(FormState.num_list_stage)
async def num_task(msg: Message, state: FSMContext):
    await state.clear()
    user_id = str(msg.from_user.id)
    list_task = load_data(LIST_FILE)
    try:
        list_task["task_s"][user_id] = int(msg.text.strip())
        if 0 < list_task["task_s"][user_id] <= len(list_task["list_tasks"][user_id]):
            save_data(LIST_FILE, list_task)
            await msg.answer('Напиши на что её заменить')
            await state.set_state(FormState.change_list_stage)
        else:
            await msg.answer('Нет задачи с таким номером, попробуй ещё раз')
    except:
        await msg.answer('Что-то пошло не так, необходимо было ввести число')

@dp.message(FormState.change_list_stage)
async def change_task(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    text1 = msg.text.strip()
    list_task = load_data(LIST_FILE)
    try:
        list_task["list_tasks"][user_id][list_task["task_s"][user_id] - 1] = text1
        await msg.answer('Задача заменена')
    except:
        await msg.answer('Что-то пошло не так')
    await state.clear()
    save_data(LIST_FILE, list_task)
    todo_list_text = "Ваш список дел:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_task["list_tasks"][user_id]))
    try:
        await bot.unpin_chat_message(chat_id=msg.chat.id)
    except:
        pass
    sent_message = await msg.answer(todo_list_text)
    await bot.pin_chat_message(chat_id=user_id, message_id=sent_message.message_id)

@dp.message(CommandStart())
async def command_start_handler(msg: Message):
    try:
        user_id = str(msg.from_user.id)
        add_user(user_id)
    except:pass
    await msg.answer('Меня зовут Маргарита, и я здесь, чтобы помочь тебе стать лучше. Согласись, что вдвоем это делать не так сложно. Будем строить планы и ставить цели!')
    await msg.answer('Выбирай действия в /actions и начинай работать над собой!')

@dp.message(Command("actions"))
async def actions(msg: Message):
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.add(InlineKeyboardButton(text="Составить список дел и планов на сегодня", callback_data="list_tasks"))
    keyboard_builder.add(InlineKeyboardButton(text="Изменение списка дел", callback_data="change_list"))
    keyboard_builder.add(InlineKeyboardButton(text="Подвести итог дня", callback_data="end_day"))
    keyboard_builder.add(InlineKeyboardButton(text="Цели на месяц", callback_data="month"))
    keyboard_builder.add(InlineKeyboardButton(text="Цели на год", callback_data="year"))
    keyboard_builder.add(InlineKeyboardButton(text="Список проблем", callback_data="problems"))
    keyboard_builder.add(InlineKeyboardButton(text="Записать мысли", callback_data="thought"))
    keyboard_builder.add(InlineKeyboardButton(text="Помощь в принятии решений", callback_data="decision"))
    keyboard_builder.adjust(1)
    await msg.answer("С чего начнем?",reply_markup=keyboard_builder.as_markup(),)

@dp.callback_query(lambda c: c.data in ["list_tasks", "change_list", "end_day", "month", "year", "problems", "thought", "decision"])
async def process_status_selection(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    list_task = load_data(LIST_FILE)
    if callback.data == "list_tasks":
        try:
            if user_id in list_task["list_tasks"] and len(list_task["list_tasks"][user_id]) != 0:
                    await callback.message.answer("У тебя уже есть список на сегодня, ты можешь просто его изменить в /actions")
                    keyboard_builder1 = InlineKeyboardBuilder()
                    keyboard_builder1.add(InlineKeyboardButton(text="Да", callback_data="yes"))
                    keyboard_builder1.add(InlineKeyboardButton(text="Нет", callback_data="no"))
                    await callback.message.answer("Хочешь создать новый список вместо этого?", reply_markup=keyboard_builder1.as_markup(), )
            else:
                list_task["list_tasks"][user_id] = []
                list_task["count_list"][user_id] = 0
                list_task["count_task"][user_id] = 0
                list_task["main_goal"][user_id] = ""
                save_data(LIST_FILE, list_task)
                await callback.message.answer("Присылай мне задачи по одной. Напиши 'готово', когда закончишь")
                await state.set_state(FormState.list_stage)
                await callback.answer()
        except:
            list_task["list_tasks"][user_id] = []
            list_task["count_list"][user_id] = 0
            list_task["count_task"][user_id] = 0
            list_task["main_goal"][user_id] = ""
            save_data(LIST_FILE, list_task)
            await callback.message.answer("Присылай мне задачи по одной. Напиши 'готово', когда закончишь")
            await state.set_state(FormState.list_stage)
            await callback.answer()
    elif callback.data == "change_list":
        keyboard_builder2 = InlineKeyboardBuilder()
        keyboard_builder2.add(InlineKeyboardButton(text="Добавить задачу", callback_data="add_task"))
        keyboard_builder2.add(InlineKeyboardButton(text="Выполнить задачу", callback_data="finish_task"))
        keyboard_builder2.add(InlineKeyboardButton(text="Изменить задачу", callback_data="change_task"))
        keyboard_builder2.add(InlineKeyboardButton(text="Удалить задачу", callback_data="del_task"))
        keyboard_builder2.adjust(1)
        await callback.message.answer("Что делаем?", reply_markup=keyboard_builder2.as_markup(), )
    elif callback.data == "end_day":
        try:
            if len(list_task["list_great_tasks"][user_id]) != 0:
                todo_list_text = "Ты молодец! За сегодня ты сделал:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_task["list_great_tasks"][user_id]))
                try:
                    await bot.unpin_chat_message(chat_id=callback.message.chat.id)
                except:pass
                await callback.message.answer(todo_list_text)
                process_t = round((list_task["count_task"][user_id] / list_task["count_list"][user_id]) * 100)
                await callback.message.answer(f"А это {process_t}% от всех поставленных задач!")
                if list_task["main_goal"][user_id] in list_task["list_great_tasks"]:
                    await callback.message.answer(f"Была выполнена главная цель на день: {list_task["main_goal"][user_id]}")
            else:
                await callback.message.answer("К сожалению, сегодня ты не выполнял задачи, завтра обязательно будь активнее!")
        except:
            await callback.message.answer("К сожалению, сегодня ты не выполнял задачи, завтра обязательно будь активнее!")

        if user_id in list_task["list_finish"]:
            if len(list_task["list_finish"][user_id]) != 0:
                await callback.message.answer(f"Сегодня особенный день, ведь ты стал намного лучше, чем вчера")
                await callback.message.answer(f"Посмотрим какие цели были достигнуты, а проблемы решены")
                list_finish_task = "Ты молодец! Ты справился с:\n" + "\n".join(f"{i + 1}. {task}" for i, task in enumerate(list_task["list_finish"][user_id]))
                await callback.message.answer(list_finish_task)

        formatted_date = datetime.date.today().strftime("%d-%m-%Y")
        configuration = load_data(END_FILE)

        if user_id in configuration:
            try:
                if configuration[user_id][str(formatted_date)]:
                    await callback.message.answer("Ты уже заполнял итог за сегодня, забыл?")
                else:
                    await callback.message.answer("Как ты себя сегодня чувствуешь? Давай сделаем небольшую заметку. Опиши каким для тебя был этот день, что ты делал и просто поделись впечатлениями, буквально на 5-7 предложений")
                    await state.set_state(FormState.text)
            except:
                await callback.message.answer(
                    "Как ты себя сегодня чувствуешь? Давай сделаем небольшую заметку. Опиши каким для тебя был этот день, что ты делал и просто поделись впечатлениями, буквально на 5-7 предложений")
                await state.set_state(FormState.text)
        await callback.answer()

    elif callback.data == "month":
        keyboard_builder3 = InlineKeyboardBuilder()
        keyboard_builder3.add(InlineKeyboardButton(text="Посмотреть цели на месяц", callback_data="show_purp_month"))
        keyboard_builder3.add(InlineKeyboardButton(text="Добавить цель на месяц", callback_data="add_purp_month"))
        keyboard_builder3.add(InlineKeyboardButton(text="Завершить цель на месяц", callback_data="finish_purp_month"))
        keyboard_builder3.add(InlineKeyboardButton(text="Удалить цель на месяц", callback_data="del_purp_month"))
        keyboard_builder3.adjust(1)
        await callback.message.answer("Что делаем?", reply_markup=keyboard_builder3.as_markup(), )
        await callback.answer()
    elif callback.data == "year":
        keyboard_builder3 = InlineKeyboardBuilder()
        keyboard_builder3.add(InlineKeyboardButton(text="Посмотреть цели на год", callback_data="show_purp_year"))
        keyboard_builder3.add(InlineKeyboardButton(text="Добавить цель на год", callback_data="add_purp_year"))
        keyboard_builder3.add(InlineKeyboardButton(text="Завершить цель на год", callback_data="finish_purp_year"))
        keyboard_builder3.add(InlineKeyboardButton(text="Удалить цель на год", callback_data="del_purp_year"))
        keyboard_builder3.adjust(1)
        await callback.message.answer("Что делаем?", reply_markup=keyboard_builder3.as_markup(), )
        await callback.answer()
    elif callback.data == "problems":
        keyboard_builder3 = InlineKeyboardBuilder()
        keyboard_builder3.add(InlineKeyboardButton(text="Посмотреть список проблем", callback_data="show_problems"))
        keyboard_builder3.add(InlineKeyboardButton(text="Добавить проблему", callback_data="add_problems"))
        keyboard_builder3.add(InlineKeyboardButton(text="Избавиться от проблемы", callback_data="finish_problems"))
        keyboard_builder3.add(InlineKeyboardButton(text="Удалить проблему", callback_data="del_problems"))
        keyboard_builder3.adjust(1)
        await callback.message.answer("Что делаем?", reply_markup=keyboard_builder3.as_markup(), )
        await callback.answer()
    elif callback.data == "thought":
        await callback.message.answer("Пришли интересные мысли? Давай их сохраним, присылай")
        await state.set_state(FormState.new_thought)
    elif callback.data == "decision":
        await callback.message.answer("Задай вопрос, на который можно ответить да или нет")
        await state.set_state(FormState.question)
        await callback.answer()

@dp.callback_query(lambda c: c.data in ["show_problems", "add_problems", "finish_problems", "del_problems"])
async def process_change_problems(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    status = load_data(LIST_FILE)
    if callback.data == "show_problems":
        ans = show_problem(user_id)
        if ans == 0:
            await callback.message.answer("Ты ещё не делился со мной проблемами")
        else:
            await callback.message.answer(ans)
        await callback.answer()
    elif callback.data == "add_problems":
        await callback.message.answer("Что ж, какую проблему мы будем уничтожать?")
        await state.set_state(FormState.add_problems)
        await callback.answer()
    elif callback.data == "finish_problems":
        ans = show_problem(user_id)
        if ans == 0:
            await callback.message.answer("Ты ещё не делился со мной проблемами")
        else:
            await callback.message.answer(ans)
            await callback.message.answer("Невероятно, ты решил проблему, которая тебя мучила, поздравляю с такой большой победой!")
            await callback.message.answer("Какую из проблем отмечаем? Напиши её номер")
            status["status"][user_id] = 1
            save_data(LIST_FILE, status)
            await state.set_state(FormState.finish_problems)
        await callback.answer()
    elif callback.data == "del_problems":
        ans = show_problem(user_id)
        if ans == 0:
            await callback.message.answer("Ты ещё не делился со мной проблемами")
        else:
            await callback.message.answer(ans)
            await callback.message.answer("Жаль, что ты решил удалить проблему, а не решить, хотя видимо на то есть причины")
            await callback.message.answer("Какую из проблем удалить? Напиши её номер")
            status["status"][user_id] = 0
            save_data(LIST_FILE, status)
            await state.set_state(FormState.finish_problems)
        await callback.answer()

@dp.callback_query(lambda c: c.data in ["show_purp_month", "add_purp_month", "finish_purp_month", "del_purp_month"])
async def process_change_month(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    status = load_data(LIST_FILE)
    if callback.data == "show_purp_month":
        ans = show_month(user_id)
        if ans == 0:
            await callback.message.answer("У тебя ещё не поставлены цели на месяц")
        else:
            await callback.message.answer(ans)
        await callback.answer()
    elif callback.data == "add_purp_month":
        await callback.message.answer("Отлично, какую цель ставим?")
        await state.set_state(FormState.add_month_purpose)
        await callback.answer()
    elif callback.data == "finish_purp_month":
        ans = show_month(user_id)
        if ans == 0:
            await callback.message.answer("У тебя ещё не поставлены цели на месяц")
        else:
            await callback.message.answer(ans)
            await callback.message.answer("Невероятно, ты достиг своей цели, поздравляю с такой большой победой!")
            await callback.message.answer("Какую из целей отмечаем? Напиши её номер")
            status["status"][user_id] = 1
            save_data(LIST_FILE, status)
            await state.set_state(FormState.finish_month_purpose)
        await callback.answer()
    elif callback.data == "del_purp_month":
        ans = show_month(user_id)
        if ans == 0:
            await callback.message.answer("У тебя ещё не поставлены цели на месяц")
        else:
            await callback.message.answer(ans)
            await callback.message.answer("Жаль, что ты решил удалить цель, хотя видимо на то есть причины")
            await callback.message.answer("Какую из целей удалить? Напиши её номер")
            status["status"][user_id] = 0
            save_data(LIST_FILE, status)
            await state.set_state(FormState.finish_month_purpose)
        await callback.answer()

@dp.callback_query(lambda c: c.data in ["show_purp_year", "add_purp_year", "finish_purp_year", "del_purp_year"])
async def process_change_year(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    status = load_data(LIST_FILE)
    if callback.data == "show_purp_year":
        ans = show_year(user_id)
        if ans == 0:
            await callback.message.answer("У тебя ещё не поставлены цели на год")
        else:
            await callback.message.answer(ans)
        await callback.answer()
    elif callback.data == "add_purp_year":
        await callback.message.answer("Отлично, какую цель на год ставим?")
        await state.set_state(FormState.add_year_purpose)
        await callback.answer()
    elif callback.data == "finish_purp_year":
        ans = show_year(user_id)
        if ans == 0:
            await callback.message.answer("У тебя ещё не поставлены цели на год")
        else:
            await callback.message.answer(ans)
            await callback.message.answer("Невероятно, ты достиг своей цели, поздравляю с такой большой победой!")
            await callback.message.answer("Какую из целей отмечаем? Напиши её номер")
            status["status"][user_id] = 1
            save_data(LIST_FILE, status)
            await state.set_state(FormState.finish_year_purpose)
        await callback.answer()
    elif callback.data == "del_purp_year":
        ans = show_year(user_id)
        if ans == 0:
            await callback.message.answer("У тебя ещё не поставлены цели на год")
        else:
            await callback.message.answer(ans)
            await callback.message.answer("Жаль, что ты решил удалить цель, хотя видимо на то есть причины")
            await callback.message.answer("Какую из целей удалить? Напиши её номер")
            status["status"][user_id] = 0
            save_data(LIST_FILE, status)
            await state.set_state(FormState.finish_year_purpose)
        await callback.answer()

@dp.callback_query(lambda c: c.data in ["add_task", "finish_task", "change_task", "del_task"])
async def process_change_list(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    status = load_data(LIST_FILE)
    try:
        if len(status["list_tasks"][user_id]) != 0:
            if callback.data == "add_task":
                await callback.message.answer("Напиши задачу и её номер числом в списке через запятую")
                await state.set_state(FormState.add_list_stage)
                await callback.answer()
            elif callback.data == "finish_task":
                await callback.message.answer("Ух-ты, здорово, задачи выполняются. Напиши номер выполненной задачи числом")
                status["status"][user_id] = 1
                save_data(LIST_FILE, status)
                await state.set_state(FormState.finish_list_stage)
                await callback.answer()
            elif callback.data == "del_task":
                await callback.message.answer("Хорошо, напиши числом номер задачи, которую нужно удалить")
                status["status"][user_id] = 0
                save_data(LIST_FILE, status)
                await state.set_state(FormState.finish_list_stage)
                await callback.answer()
            elif callback.data == "change_task":
                await callback.message.answer("Хорошо, напиши числом номер задачи, которую хочешь заменить")
                await state.set_state(FormState.num_list_stage)
                await callback.answer()
        else:
            await callback.message.answer("У тебя ещё нет списка дел на сегодня, создай его скорее")
    except:
        await callback.message.answer("У тебя ещё нет списка дел на сегодня, создай его скорее")

@dp.callback_query(lambda c: c.data in ["yes", "no"])
async def process_status_selection(callback: CallbackQuery, state: FSMContext):
    user_id = str(callback.from_user.id)
    list_task = load_data(LIST_FILE)
    if callback.data == "yes":
        await callback.message.answer("Хорошо")
        list_task["list_tasks"][user_id].clear()
        list_task["count_list"][user_id] = 0
        list_task["count_task"][user_id] = 0
        list_task["main_goal"][user_id] = ""
        save_data(LIST_FILE, list_task)
        await callback.message.answer("Присылай мне задачи по одной. Напиши 'готово', когда закончишь")
        await state.set_state(FormState.list_stage)
        await callback.answer()
    elif callback.data == 'no':
        await callback.message.answer("Хорошо")

@dp.message(Command("list"))
async def list_t(msg: Message):
    keyboard_builder = InlineKeyboardBuilder()
    user_id = str(msg.from_user.id)
    configuration = load_data(END_FILE)

    if user_id in configuration and configuration[user_id]:
        for dat in configuration[user_id]:
            keyboard_builder.add(InlineKeyboardButton(text=f"{dat}", callback_data=f"show_text:{dat}"))
        keyboard_builder.adjust(1)
        await msg.answer("Выбери дату",reply_markup=keyboard_builder.as_markup(),)
    else:
        await msg.answer("У тебя ещё нет записей, для этого необходимо подводить итоги дня")

@dp.callback_query(F.data.startswith("show_text:"))
async def callback_show_text(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    day = str(callback.data.split(":")[1])
    configuration = load_data(END_FILE)
    text_r = configuration[user_id][day]
    await callback.message.answer(text=f"Запись за {day}: {text_r}")
    await callback.answer()

@dp.message(Command("info"))
async def info(msg: Message):
    await msg.answer("Я – Маргарита, и моя задача – помочь тебе раскрыть свой потенциал. Я предлагаю инструменты для планирования и целеполагания")
    await msg.answer('Давай составим твой список дел на сегодня')
    await msg.answer('Выбирай действия в /actions и начинай работать над собой!')

@dp.message(Command("list_thought"))
async def list_thought(msg: Message):
    keyboard_builder = InlineKeyboardBuilder()
    user_id = str(msg.from_user.id)
    configuration = load_data(NEW_FILE)

    if user_id in configuration:
        for date in configuration[user_id]:
            keyboard_builder.add(InlineKeyboardButton(text=f"{date}", callback_data=f"new_thought:{date}"))
        keyboard_builder.adjust(1)
        await msg.answer("Выбери заметку",reply_markup=keyboard_builder.as_markup(),)
    else:
        await msg.answer("У тебя ещё нет записей")

@dp.callback_query(F.data.startswith("new_thought:"))
async def callback_new_thought(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    day = str(callback.data.split(":")[1])
    configuration = load_data(NEW_FILE)
    text_e = configuration[user_id][day]
    await callback.message.answer(text=f"Запись {day}: {text_e}")
    await callback.answer()

@dp.message(Command("task"))
async def task_t(msg: Message, state: FSMContext):
    now = datetime.datetime.now()

    if now.day == 27:
        user_id = str(msg.from_user.id)
        configuration = load_data(TASK_FILE)
        if not configuration[user_id][str(now.date())]:
            await msg.answer("Составь список из 10 пунктов, в которых опиши за что ты себя любишь и за что себе благодарен. Это могут быть любые качества, поступки, мечты и другие факты. Хорошенько подумай и отправляй мне одним сообщением!")
            await state.set_state(FormState.task_month)
        else:
            await msg.answer("Ты уже выполнял сегодня ежемесячное задание, но если хочешь изменить его, то отправляй список, а если не хочешь, то напиши 'нет'")
            await state.set_state(FormState.task_month)
    else:
        await msg.answer("Ещё рано для выполнения ежемесячного задания, я обязательно тебе об этом напомню")

@dp.message(Command("task_month"))
async def task_month(msg: Message):
    keyboard_builder = InlineKeyboardBuilder()
    user_id = str(msg.from_user.id)
    configuration = load_data(TASK_FILE)

    if user_id in configuration:
        for date in configuration[user_id]:
            keyboard_builder.add(InlineKeyboardButton(text=f"{date}", callback_data=f"task_month:{date}"))
        keyboard_builder.adjust(1)
        await msg.answer("Выбери задание",reply_markup=keyboard_builder.as_markup(),)
    else:
        await msg.answer("У тебя ещё нет заданий")

@dp.callback_query(F.data.startswith("task_month:"))
async def callback_new_thought(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    day = str(callback.data.split(":")[1])
    configuration = load_data(TASK_FILE)
    await callback.message.answer(text=f"{configuration[user_id][day]}")
    await callback.answer()

@dp.message(Command("change_main"))
async def change_main(msg: Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    list_tasks = load_data(LIST_FILE)
    if user_id in list_tasks["list_tasks"]:
        if len(list_tasks["list_tasks"][user_id]) != 0:
            await msg.answer("Давай теперь выберем самую важную цель на сегодня, на которой у нас будет фокус. Напиши номер этой задачи числом")
            await state.set_state(FormState.main_goal)
        else:
            await msg.answer("Ваш список дел пуст")
    else:
        await msg.answer("Ваш список дел пуст")

@dp.message(Command("set_birthday"))
async def set_birthday(msg: Message, state: FSMContext):
    await msg.answer("Введи свой день рождения в формате день-месяц-год")
    await state.set_state(FormState.set_birthday)

async def scheduler():
    while True:
        now = datetime.datetime.now()
        user_ids = get_all_user_ids()

        # Уведомление в 9:00
        if now.hour == 9 and now.minute == 0:
            line_number = random.randint(1, 76)
            text_msg = linecache.getline('morning.txt', line_number).strip()
            for user_id in user_ids:
                try:
                    await bot.send_message(user_id, text=text_msg)
                    await asyncio.sleep(0.05)
                except:pass
            await asyncio.sleep(60)
        # Уведомление в 23:00
        if now.hour == 23 and now.minute == 0:
            line_number = random.randint(1, 90)
            text_msg = linecache.getline('night.txt', line_number).strip()
            for user_id in user_ids:
                try:
                    await bot.send_message(user_id, text=text_msg)
                    await asyncio.sleep(0.05)
                except:
                    pass
            await asyncio.sleep(60)
        # сброс всего
        if now.hour == 15 and now.minute == 34:
            lists = load_data(LIST_FILE)
            for user_id in user_ids:
                user_id = str(user_id)
                try:
                    lists["list_tasks"][user_id].clear()
                    lists["list_great_tasks"][user_id].clear()
                    lists["list_finish"][user_id].clear()
                    lists["count_list"][user_id] = 0
                    lists["count_task"][user_id] = 0
                    lists["status"][user_id] = 0
                    lists["task_s"][user_id] = 0
                    lists["main_goal"][user_id] = ""
                    await bot.send_message(user_id, text="Ваши списки на сегодня были сброшены, увидимся завтра")
                    await asyncio.sleep(0.05)
                except:pass
            save_data(LIST_FILE, lists)
            await asyncio.sleep(60)
        # Ежемесячное задание
        if now.hour == 14 and now.minute == 0 and now.day == 27:
            for user_id in user_ids:
                try:
                    await bot.send_message(user_id, text="Давай сделаем небольшое ежемесячное задание, жми /task")
                except:pass
            await asyncio.sleep(60)
        await asyncio.sleep(60)

async def birth():
    while True:
        now = datetime.datetime.now()
        user_ids = get_all_user_ids()
        lis = load_data(LIST_FILE)
        try:
            for user in user_ids:
                user = str(user)
                k = lis["set_birthday"][user]
                birt = datetime.datetime.strptime(k, "%d-%m-%Y")
                if birt.day == now.day and birt.month == now.month and (now.hour == 7 or now.hour == 8):
                    await bot.send_message(user, text="С Днём Рождения! Верь в себя! Стремись к лучшему! Достигай целей! Сегодня твой день! Сделай его незабываемым!")
        except:pass
        await asyncio.sleep(3600)

async def goals():
    while True:
        now = datetime.datetime.now()
        user_ids = get_all_user_ids()
        lis = load_data(LIST_FILE)
        for user in user_ids:
            user = str(user)
            if user in lis["list_date_month"]:
                if len(lis["list_date_month"][user]) != 0:
                    for i in lis["list_date_month"][user]:
                        k = datetime.datetime.strptime(i, "%d-%m-%Y")
                        if k.day == now.day and k.month == now.month:
                            num = lis["list_date_month"][user].index(i)
                            keyboard_builder1 = InlineKeyboardBuilder()
                            keyboard_builder1.add(InlineKeyboardButton(text="Продлить на ещё один месяц", callback_data="one"))
                            keyboard_builder1.add(InlineKeyboardButton(text="Отметить выполненной", callback_data="two"))
                            keyboard_builder1.add(InlineKeyboardButton(text="Удалить", callback_data="three"))
                            keyboard_builder1.adjust(1)
                            await bot.send_message(user,f"30 дней назад ты поставил цель: {lis["list_purpose_month"][user][num]}, но не отметил её, что делать?",
                                                   reply_markup=keyboard_builder1.as_markup(), )
            if user in lis["list_date_year"]:
                if len(lis["list_date_year"][user]) != 0:
                    for i in lis["list_date_year"][user]:
                        k = datetime.datetime.strptime(i, "%d-%m-%Y")
                        if k.day == now.day and k.month == now.month and k.year == now.year:
                            num = lis["list_date_year"][user].index(i)
                            keyboard_builder1 = InlineKeyboardBuilder()
                            keyboard_builder1.add(InlineKeyboardButton(text="Продлить на один месяц", callback_data="one_y"))
                            keyboard_builder1.add(InlineKeyboardButton(text="Отметить выполненной", callback_data="two_y"))
                            keyboard_builder1.add(InlineKeyboardButton(text="Удалить", callback_data="three_y"))
                            keyboard_builder1.adjust(1)
                            await bot.send_message(user,f"Год назад ты поставил цель: {lis["list_purpose_year"][user][num]}, но не отметил её, что делать?",
                                                   reply_markup=keyboard_builder1.as_markup(), )
        await asyncio.sleep(86400)

@dp.callback_query(lambda c: c.data in ["one", "two", "three"])
async def process_change(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    if callback.data == "one":
        now = datetime.datetime.now()
        lis = load_data(LIST_FILE)
        future_date = datetime.datetime.now() + datetime.timedelta(days=30)
        formatted_date = future_date.strftime("%d-%m-%Y")
        for i in lis["list_date_month"][user_id]:
            k = datetime.datetime.strptime(i, "%d-%m-%Y")
            task1 = lis["list_date_month"][user_id].index(i)
            if k.day == now.day and k.month == now.month:
                lis["list_date_month"][user_id][task1] = formatted_date
                await callback.message.answer(f"У тебя есть ещё 30 дней, справься до {formatted_date}")
        save_data(LIST_FILE, lis)
        await callback.answer()
    elif callback.data == "two":
        now = datetime.datetime.now()
        lis = load_data(LIST_FILE)
        for i in lis["list_date_month"][user_id]:
            k = datetime.datetime.strptime(i, "%d-%m-%Y")
            task1 = lis["list_date_month"][user_id].index(i)
            if k.day == now.day and k.month == now.month:
                lis["list_finish"][user_id].append(lis["list_purpose_month"][user_id][task1])
                del lis["list_purpose_month"][user_id][task1]
                del lis["list_date_month"][user_id][task1]
                save_data(LIST_FILE, lis)

        await callback.message.answer("Поздравляю с достижением ещё одной цели!")
        await callback.answer()
    elif callback.data == "three":
        now = datetime.datetime.now()
        lis = load_data(LIST_FILE)
        for i in lis["list_date_month"][user_id]:
            k = datetime.datetime.strptime(i, "%d-%m-%Y")
            task1 = lis["list_date_month"][user_id].index(i)
            if k.day == now.day and k.month == now.month:
                del lis["list_purpose_month"][user_id][task1]
                del lis["list_date_month"][user_id][task1]
                save_data(LIST_FILE, lis)
        await callback.message.answer("Цель была удалена")
        await callback.answer()

@dp.callback_query(lambda c: c.data in ["one_y", "two_y", "three_y"])
async def process_change(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    if callback.data == "one_y":
        now = datetime.datetime.now()
        lis = load_data(LIST_FILE)
        future_date = datetime.datetime.now() + datetime.timedelta(days=30)
        formatted_date = future_date.strftime("%d-%m-%Y")
        for i in lis["list_date_year"][user_id]:
            k = datetime.datetime.strptime(i, "%d-%m-%Y")
            task1 = lis["list_date_year"][user_id].index(i)
            if k.day == now.day and k.month == now.month and k.year == now.year:
                lis["list_date_year"][user_id][task1] = formatted_date
                await callback.message.answer(f"У тебя есть ещё 30 дней, справься до {formatted_date}")
        save_data(LIST_FILE, lis)
        await callback.answer()
    elif callback.data == "two_y":
        now = datetime.datetime.now()
        lis = load_data(LIST_FILE)
        for i in lis["list_date_year"][user_id]:
            k = datetime.datetime.strptime(i, "%d-%m-%Y")
            task1 = lis["list_date_year"][user_id].index(i)
            if k.day == now.day and k.month == now.month:
                lis["list_finish"][user_id].append(lis["list_purpose_year"][user_id][task1])
                del lis["list_purpose_year"][user_id][task1]
                del lis["list_date_year"][user_id][task1]
                save_data(LIST_FILE, lis)

        await callback.message.answer("Поздравляю с достижением ещё одной цели!")
        await callback.answer()
    elif callback.data == "three_y":
        now = datetime.datetime.now()
        lis = load_data(LIST_FILE)
        for i in lis["list_date_year"][user_id]:
            k = datetime.datetime.strptime(i, "%d-%m-%Y")
            task1 = lis["list_date_year"][user_id].index(i)
            if k.day == now.day and k.month == now.month:
                del lis["list_purpose_year"][user_id][task1]
                del lis["list_date_year"][user_id][task1]
                save_data(LIST_FILE, lis)
        await callback.message.answer("Цель была удалена")
        await callback.answer()

async def main() -> None:
    create_db()
    asyncio.create_task(scheduler())
    asyncio.create_task(birth())
    asyncio.create_task(goals())
    await set_commands()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
