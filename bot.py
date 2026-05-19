import os
import re
from io import BytesIO
from datetime import datetime

import pandas as pd
import requests
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_URL = os.getenv("SHEET_URL")

LANG_BUTTONS = {
    "🇺🇦 Українська": "ua",
    "🇵🇱 Polski": "pl",
    "🇬🇧 English": "en",
    "🇪🇸 Español": "es",
    "🇷🇺 Русский": "ru",
}

TEXTS = {
    "ua": {
        "choose_lang": "Оберіть мову:",
        "welcome": "Привіт 👋\nЯ віртуальний помічник MeGreat.\nОберіть, з чим Вам допомогти:",
        "main": "ГОЛОВНЕ МЕНЮ",
        "payments_button": "💳 Хочу оплатити оплату скарбову",
        "choose_voivodeship": "Оберіть воєводство:",
        "what_payment": "За що платимо?",
        "temporary": "Тимчасове перебування",
        "permanent": "Постійне перебування",
        "resident": "Резидент ЄС",
        "citizenship": "Громадянство",
        "card_print": "Друк карти побиту",
        "proxy": "Доручення",
        "work_question": "Чи по роботі?",
        "yes_work": "ТАК, по роботі",
        "no_work": "НІ, не по роботі",
        "basis_question": "Оберіть підставу:",
        "karta_polaka": "На підставі карти Поляка",
        "no_karta_polaka": "Без карти Поляка",
        "card_type": "Оберіть тип карти:",
        "cukr": "Карта CUKR",
        "traditional_card": "Karta Pobytu tradycyjna (Nie CUKR)",
        "discount_question": "Оберіть варіант:",
        "adult_no_discount": "Повнолітня особа без пільг",
        "discount": "Пільгова оплата",
        "enter_name": "Введіть ім’я та прізвище заявника ЛАТИНСЬКИМИ літерами.\nНаприклад: IVAN PETRENKO",
        "enter_birth": "Введіть дату народження у форматі ДД.ММ.РРРР.\nНаприклад: 01.01.1990",
        "enter_proxy": "Введіть ім’я та прізвище довіреної особи ЛАТИНСЬКИМИ літерами.\nНаприклад: ANNA KOWALSKA",
        "invalid_name": "⚠️ Введіть ім’я та прізвище тільки латинськими літерами.",
        "invalid_date": "⚠️ Невірна дата народження.",
        "choose_button": "Оберіть варіант з кнопок.",
        "restart": "🔄 Почати спочатку",
    },
    "pl": {
        "choose_lang": "Wybierz język:",
        "welcome": "Cześć 👋\nJestem wirtualnym asystentem MeGreat.\nWybierz, w czym mogę pomóc:",
        "main": "MENU GŁÓWNE",
        "payments_button": "💳 Chcę opłacić opłatę skarbową",
        "choose_voivodeship": "Wybierz województwo:",
        "what_payment": "Za co chcesz zapłacić?",
        "temporary": "Pobyt czasowy",
        "permanent": "Pobyt stały",
        "resident": "Rezydent UE",
        "citizenship": "Obywatelstwo",
        "card_print": "Wydanie karty pobytu",
        "proxy": "Pełnomocnictwo",
        "work_question": "Czy w związku z pracą?",
        "yes_work": "TAK, praca",
        "no_work": "NIE, bez pracy",
        "basis_question": "Wybierz podstawę:",
        "karta_polaka": "Na podstawie Karty Polaka",
        "no_karta_polaka": "Bez Karty Polaka",
        "card_type": "Wybierz typ karty:",
        "cukr": "Karta CUKR",
        "traditional_card": "Karta Pobytu tradycyjna (Nie CUKR)",
        "discount_question": "Wybierz wariant:",
        "adult_no_discount": "Osoba pełnoletnia bez ulgi",
        "discount": "Opłata ulgowa",
        "enter_name": "Wpisz imię i nazwisko literami łacińskimi.\nPrzykład: IVAN PETRENKO",
        "enter_birth": "Wpisz datę urodzenia w formacie DD.MM.RRRR.\nPrzykład: 01.01.1990",
        "enter_proxy": "Wpisz imię i nazwisko pełnomocnika literami łacińskimi.\nPrzykład: ANNA KOWALSKA",
        "invalid_name": "⚠️ Wpisz imię i nazwisko tylko literami łacińskimi.",
        "invalid_date": "⚠️ Nieprawidłowa data urodzenia.",
        "choose_button": "Wybierz wariant z przycisków.",
        "restart": "🔄 Zacznij od początku",
    },
    "en": {
        "choose_lang": "Choose language:",
        "welcome": "Cześć 👋\nJestem wirtualnym asystentem MeGreat.\nWybierz, w czym mogę pomóc:",
        "main": "MENU GŁÓWNE",
        "payments_button": "💳 Chcę opłacić opłatę skarbową",
        "choose_voivodeship": "Choose the voivodeship:",
        "what_payment": "What are you paying for?",
        "temporary": "Temporary residence",
        "permanent": "Permanent residence",
        "resident": "EU long-term resident",
        "citizenship": "Citizenship",
        "card_print": "Residence card printing",
        "proxy": "Power of attorney",
        "work_question": "Is it work-related?",
        "yes_work": "YES, work-related",
        "no_work": "NO, not work-related",
        "basis_question": "Choose the basis:",
        "karta_polaka": "Based on the Pole’s Card",
        "no_karta_polaka": "Without the Pole’s Card",
        "card_type": "Choose card type:",
        "cukr": "CUKR card",
        "traditional_card": "Traditional residence card, not CUKR",
        "discount_question": "Choose option:",
        "adult_no_discount": "Adult without discount",
        "discount": "Discounted fee",
        "enter_name": "Enter applicant’s name and surname using LATIN letters.\nExample: IVAN PETRENKO",
        "enter_birth": "Enter date of birth in DD.MM.YYYY format.\nExample: 01.01.1990",
        "enter_proxy": "Enter proxy’s name and surname using LATIN letters.\nExample: ANNA KOWALSKA",
        "invalid_name": "⚠️ Use Latin letters only.",
        "invalid_date": "⚠️ Invalid date of birth.",
        "choose_button": "Choose an option from the buttons.",
        "restart": "🔄 Start again",
    },
    "es": {
        "choose_lang": "Elige el idioma:",
        "welcome": "Hola 👋\nSoy el asistente virtual de MeGreat.\nElige cómo puedo ayudarte:",
        "main": "MENÚ PRINCIPAL",
        "payments_button": "💳 Quiero pagar una tasa oficial",
        "choose_voivodeship": "Elige el voivodato:",
        "what_payment": "¿Por qué quieres pagar?",
        "temporary": "Residencia temporal",
        "permanent": "Residencia permanente",
        "resident": "Residente de larga duración UE",
        "citizenship": "Ciudadanía",
        "card_print": "Impresión de tarjeta de residencia",
        "proxy": "Poder / autorización",
        "work_question": "¿Es por trabajo?",
        "yes_work": "SÍ, por trabajo",
        "no_work": "NO, no por trabajo",
        "basis_question": "Elige la base:",
        "karta_polaka": "Con la Tarjeta del Polaco",
        "no_karta_polaka": "Sin la Tarjeta del Polaco",
        "card_type": "Elige el tipo de tarjeta:",
        "cukr": "Tarjeta CUKR",
        "traditional_card": "Tarjeta de residencia tradicional, no CUKR",
        "discount_question": "Elige una opción:",
        "adult_no_discount": "Adulto sin descuento",
        "discount": "Tarifa reducida",
        "enter_name": "Introduce nombre y apellido con letras LATINAS.\nEjemplo: IVAN PETRENKO",
        "enter_birth": "Introduce la fecha de nacimiento en formato DD.MM.AAAA.\nEjemplo: 01.01.1990",
        "enter_proxy": "Introduce nombre y apellido del representante con letras LATINAS.\nEjemplo: ANNA KOWALSKA",
        "invalid_name": "⚠️ Usa solo letras latinas.",
        "invalid_date": "⚠️ Fecha de nacimiento incorrecta.",
        "choose_button": "Elige una opción de los botones.",
        "restart": "🔄 Empezar de nuevo",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "welcome": "Привет 👋\nЯ виртуальный помощник MeGreat.\nВыберите, с чем Вам помочь:",
        "main": "ГЛАВНОЕ МЕНЮ",
        "payments_button": "💳 Хочу оплатить гербовый сбор",
        "choose_voivodeship": "Выберите воеводство:",
        "what_payment": "За что платим?",
        "temporary": "Временное пребывание",
        "permanent": "Постоянное пребывание",
        "resident": "Резидент ЕС",
        "citizenship": "Гражданство",
        "card_print": "Печать карты побыта",
        "proxy": "Доверенность",
        "work_question": "По работе?",
        "yes_work": "ДА, по работе",
        "no_work": "НЕТ, не по работе",
        "basis_question": "Выберите основание:",
        "karta_polaka": "На основании Карты Поляка",
        "no_karta_polaka": "Без Карты Поляка",
        "card_type": "Выберите тип карты:",
        "cukr": "Карта CUKR",
        "traditional_card": "Обычная карта побыта, не CUKR",
        "discount_question": "Выберите вариант:",
        "adult_no_discount": "Совершеннолетний без льгот",
        "discount": "Льготная оплата",
        "enter_name": "Введите имя и фамилию заявителя ЛАТИНСКИМИ буквами.\nНапример: IVAN PETRENKO",
        "enter_birth": "Введите дату рождения в формате ДД.ММ.ГГГГ.\nНапример: 01.01.1990",
        "enter_proxy": "Введите имя и фамилию доверенного лица ЛАТИНСКИМИ буквами.\nНапример: ANNA KOWALSKA",
        "invalid_name": "⚠️ Введите имя и фамилию только латинскими буквами.",
        "invalid_date": "⚠️ Неверная дата рождения.",
        "choose_button": "Выберите вариант из кнопок.",
        "restart": "🔄 Начать сначала",
    },
}

FINAL_PAYMENTS = {
    "yes_work": {
        "payment_type_id": "pobyt_praca",
        "label": "Pobyt czasowy i praca",
        "amount": 440,
        "title": "Opłata skarbowa za zezwolenie na pobyt czasowy i pracę dla {full_name}, ur. {birth_date}",
    },
    "no_work": {
        "payment_type_id": "pobyt_czasowy",
        "label": "Pobyt czasowy",
        "amount": 340,
        "title": "Opłata skarbowa za zezwolenie na pobyt czasowy dla {full_name}, ur. {birth_date}",
    },
    "karta_polaka": {
        "payment_type_id": "pobyt_staly_karta_polaka",
        "label": "Pobyt stały na podstawie Karty Polaka",
        "amount": 0,
        "free": True,
        "title": "",
    },
    "no_karta_polaka": {
        "payment_type_id": "pobyt_staly",
        "label": "Pobyt stały",
        "amount": 640,
        "title": "Opłata skarbowa za zezwolenie na pobyt stały dla {full_name}, ur. {birth_date}",
    },
    "resident": {
        "payment_type_id": "rezydent_ue",
        "label": "Rezydent długoterminowy UE",
        "amount": 640,
        "title": "Opłata skarbowa za zezwolenie na pobyt rezydenta długoterminowego UE dla {full_name}, ur. {birth_date}",
    },
    "citizenship": {
        "payment_type_id": "obywatelstwo",
        "label": "Uznanie za obywatela polskiego",
        "amount": 1000,
        "title": "Opłata za wniosek o uznanie za obywatela polskiego dla {full_name}, ur. {birth_date}",
    },
    "cukr": {
        "payment_type_id": "karta_cukr",
        "label": "Karta CUKR",
        "amount": 100,
        "title": "Opłata za wydanie karty pobytu CUKR dla {full_name}, ur. {birth_date}",
    },
    "adult_no_discount": {
        "payment_type_id": "karta_100",
        "label": "Karta pobytu tradycyjna 100%",
        "amount": 100,
        "title": "Opłata za wydanie karty pobytu dla {full_name}, ur. {birth_date}",
    },
    "discount": {
        "payment_type_id": "karta_50",
        "label": "Karta pobytu tradycyjna 50%",
        "amount": 50,
        "title": "Opłata za wydanie karty pobytu - ulga 50% dla {full_name}, ur. {birth_date}",
    },
    "proxy": {
        "payment_type_id": "pelnomocnictwo",
        "label": "Pełnomocnictwo",
        "amount": 17,
        "needs_proxy": True,
        "title": "Opłata skarbowa od pełnomocnictwa: {proxy_name}, sprawa osoby: {full_name}, ur. {birth_date}",
    },
}


def lang(context):
    return context.user_data.get("lang", "ua")


def t(context, key):
    return TEXTS.get(lang(context), TEXTS["ua"]).get(key, key)


def sheet_export_url(url):
    match = re.search(r"/d/([^/]+)", url or "")
    if match:
        return f"https://docs.google.com/spreadsheets/d/{match.group(1)}/export?format=xlsx"
    return url


def load_database():
    response = requests.get(sheet_export_url(SHEET_URL), timeout=30)
    response.raise_for_status()
    xlsx = BytesIO(response.content)

    voivodeships = pd.read_excel(xlsx, sheet_name="voivodeships").fillna("")
    xlsx.seek(0)
    accounts = pd.read_excel(xlsx, sheet_name="accounts").fillna("")
    xlsx.seek(0)
    routes = pd.read_excel(xlsx, sheet_name="payment_routes").fillna("")

    return {
        "voivodeships": voivodeships,
        "accounts": accounts,
        "routes": routes,
    }


DB = load_database()


def make_keyboard(items, row_size=2):
    rows = []
    row = []

    for item in items:
        row.append(str(item))
        if len(row) == row_size:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def keyboard_with_restart(context, items, row_size=2):
    rows = []
    row = []

    for item in items:
        row.append(str(item))
        if len(row) == row_size:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([t(context, "restart")])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


def is_latin_name(name):
    return re.fullmatch(r"^[A-Za-zÀ-ÿ' -]+$", name.strip()) is not None


def validate_birth_date(date_text):
    try:
        birth = datetime.strptime(date_text, "%d.%m.%Y")
        today = datetime.today()

        if birth > today:
            return False

        age = today.year - birth.year
        if age > 120:
            return False

        return True
    except ValueError:
        return False


def get_voivodeship(name):
    rows = DB["voivodeships"][DB["voivodeships"]["name_pl"].astype(str).str.strip() == name.strip()]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def get_route(voivodeship_id, payment_type_id):
    routes = DB["routes"]
    rows = routes[
        (routes["voivodeship_id"].astype(str).str.strip() == str(voivodeship_id).strip())
        & (routes["payment_type_id"].astype(str).str.strip() == str(payment_type_id).strip())
    ]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def get_account(account_id):
    rows = DB["accounts"][DB["accounts"]["account_id"].astype(str).str.strip() == str(account_id).strip()]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()


def key_for_text(context, text, keys):
    for key in keys:
        if text == t(context, key):
            return key
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["step"] = "language"

    await update.message.reply_text(
        "Оберіть мову / Wybierz język / Choose language:",
        reply_markup=make_keyboard(list(LANG_BUTTONS.keys()), 1),
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    step = context.user_data.get("step")

    if text in [TEXTS[code]["restart"] for code in TEXTS]:
        return await start(update, context)

    if step == "language":
        if text not in LANG_BUTTONS:
            await update.message.reply_text("Оберіть мову з кнопок.")
            return

        context.user_data["lang"] = LANG_BUTTONS[text]
        context.user_data["step"] = "main_menu"

        await update.message.reply_text(
            t(context, "welcome"),
            reply_markup=ReplyKeyboardMarkup(
                [[t(context, "payments_button")]],
                resize_keyboard=True,
            ),
        )
        return

    if text == t(context, "payments_button"):
        context.user_data["step"] = "voivodeship"
        names = DB["voivodeships"]["name_pl"].astype(str).tolist()

        await update.message.reply_text(
            t(context, "choose_voivodeship"),
            reply_markup=keyboard_with_restart(context, names, 2),
        )
        return

    if step == "voivodeship":
        voivodeship = get_voivodeship(text)

        if not voivodeship:
            await update.message.reply_text(t(context, "choose_button"))
            return

        context.user_data["voivodeship"] = voivodeship
        context.user_data["step"] = "main_payment_category"

        await update.message.reply_text(
            t(context, "what_payment"),
            reply_markup=keyboard_with_restart(
                context,
                [
                    t(context, "temporary"),
                    t(context, "permanent"),
                    t(context, "resident"),
                    t(context, "citizenship"),
                    t(context, "card_print"),
                    t(context, "proxy"),
                ],
                1,
            ),
        )
        return

    if step == "main_payment_category":
        category = key_for_text(context, text, ["temporary", "permanent", "resident", "citizenship", "card_print", "proxy"])

        if category == "temporary":
            context.user_data["step"] = "temporary_work"
            await update.message.reply_text(
                t(context, "work_question"),
                reply_markup=keyboard_with_restart(context, [t(context, "yes_work"), t(context, "no_work")], 1),
            )
            return

        if category == "permanent":
            context.user_data["step"] = "permanent_basis"
            await update.message.reply_text(
                t(context, "basis_question"),
                reply_markup=keyboard_with_restart(context, [t(context, "karta_polaka"), t(context, "no_karta_polaka")], 1),
            )
            return

        if category == "card_print":
            context.user_data["step"] = "card_type"
            await update.message.reply_text(
                t(context, "card_type"),
                reply_markup=keyboard_with_restart(context, [t(context, "cukr"), t(context, "traditional_card")], 1),
            )
            return

        if category in ["resident", "citizenship", "proxy"]:
            context.user_data["selected_payment"] = FINAL_PAYMENTS[category]
            context.user_data["step"] = "full_name"
            await update.message.reply_text(t(context, "enter_name"))
            return

        await update.message.reply_text(t(context, "choose_button"))
        return

    if step == "temporary_work":
        selected_key = key_for_text(context, text, ["yes_work", "no_work"])

        if not selected_key:
            await update.message.reply_text(t(context, "choose_button"))
            return

        context.user_data["selected_payment"] = FINAL_PAYMENTS[selected_key]
        context.user_data["step"] = "full_name"
        await update.message.reply_text(t(context, "enter_name"))
        return

    if step == "permanent_basis":
        selected_key = key_for_text(context, text, ["karta_polaka", "no_karta_polaka"])

        if not selected_key:
            await update.message.reply_text(t(context, "choose_button"))
            return

        context.user_data["selected_payment"] = FINAL_PAYMENTS[selected_key]

        if FINAL_PAYMENTS[selected_key].get("free"):
            result = build_result(context.user_data)
            context.user_data.clear()
            await update.message.reply_text(result)
            return

        context.user_data["step"] = "full_name"
        await update.message.reply_text(t(context, "enter_name"))
        return

    if step == "card_type":
        selected_key = key_for_text(context, text, ["cukr", "traditional_card"])

        if selected_key == "cukr":
            context.user_data["selected_payment"] = FINAL_PAYMENTS["cukr"]
            context.user_data["step"] = "full_name"
            await update.message.reply_text(t(context, "enter_name"))
            return

        if selected_key == "traditional_card":
            context.user_data["step"] = "traditional_card_discount"
            await update.message.reply_text(
                t(context, "discount_question"),
                reply_markup=keyboard_with_restart(context, [t(context, "adult_no_discount"), t(context, "discount")], 1),
            )
            return

        await update.message.reply_text(t(context, "choose_button"))
        return

    if step == "traditional_card_discount":
        selected_key = key_for_text(context, text, ["adult_no_discount", "discount"])

        if not selected_key:
            await update.message.reply_text(t(context, "choose_button"))
            return

        context.user_data["selected_payment"] = FINAL_PAYMENTS[selected_key]
        context.user_data["step"] = "full_name"
        await update.message.reply_text(t(context, "enter_name"))
        return

    if step == "full_name":
        if not is_latin_name(text):
            await update.message.reply_text(t(context, "invalid_name"))
            return

        context.user_data["full_name"] = text.upper()
        context.user_data["step"] = "birth_date"

        await update.message.reply_text(t(context, "enter_birth"))
        return

    if step == "birth_date":
        if not validate_birth_date(text):
            await update.message.reply_text(t(context, "invalid_date"))
            return

        context.user_data["birth_date"] = text
        selected = context.user_data["selected_payment"]

        if selected.get("needs_proxy"):
            context.user_data["step"] = "proxy_name"
            await update.message.reply_text(t(context, "enter_proxy"))
            return

        result = build_result(context.user_data)
        context.user_data.clear()
        await update.message.reply_text(result)
        return

    if step == "proxy_name":
        if not is_latin_name(text):
            await update.message.reply_text(t(context, "invalid_name"))
            return

        context.user_data["proxy_name"] = text.upper()

        result = build_result(context.user_data)
        context.user_data.clear()
        await update.message.reply_text(result)
        return

    await update.message.reply_text("/start")


def build_result(data):
    voivodeship = data["voivodeship"]
    payment = data["selected_payment"]

    if payment.get("free"):
        return f"""
✅ Оплата не потрібна

Воєводство:
{voivodeship["name_pl"]}

Тип справи:
{payment["label"]}

📌 Сума оплати:
0 zł

Ця дія є безкоштовною.
Не виконуйте переказ.
Реквізити для оплати не потрібні.
"""

    route = get_route(voivodeship["voivodeship_id"], payment["payment_type_id"])

    if not route:
        return f"""
⚠️ У Google Sheets немає маршруту оплати.

Воєводство:
{voivodeship["name_pl"]}

Тип оплати:
{payment["label"]}

Payment type ID:
{payment["payment_type_id"]}

Додай цей payment_type_id у вкладку payment_routes.
"""

    account = get_account(route["account_id"])

    if not account:
        return "⚠️ Не знайдено рахунок у вкладці accounts."

    title = payment["title"].format(
        full_name=data.get("full_name", ""),
        birth_date=data.get("birth_date", ""),
        proxy_name=data.get("proxy_name", ""),
    )

    return f"""
✅ Дані для оплати готові

Оберіть у своєму банку звичайний переказ на рахунок.

📌 У полі «ОТРИМУВАЧ» / «ODBIORCA» встав:

{account["recipient"]}

📌 У полі «НОМЕР РАХУНКУ» / «NUMER RACHUNKU» встав:

{account["bank_account"]}

📌 У полі «СУМА ОПЛАТИ» / «KWOTA» встав:

{payment["amount"]} zł

📌 У полі «ПРИЗНАЧЕННЯ ПЛАТЕЖУ» / «TYTUŁ PRZELEWU» встав:

{title}

━━━━━━━━━━━━━━

Деталі справи:

Воєводство:
{voivodeship["name_pl"]}

Ужонд:
{voivodeship["office_name"]}

Тип оплати:
{payment["label"]}

Статус перевірки:
{route.get("verification_status", "")}

Джерело:
{route.get("source_url", "")}

⚠️ Перед оплатою перевірте реквізити на офіційній сторінці ужонду.
"""


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Bot works.")
    app.run_polling()


if __name__ == "__main__":
    main()
