import aiogram.types
from aiogram.types import Message, ContentType
from aiogram.types import PreCheckoutQuery, LabeledPrice
from aiogram.dispatcher.filters import Command
import aiogram
import sqlite3
from main import bot, dp
import json
from keyboards import keyboard
import uuid
import hashlib
import datetime
import urllib.request
import re

# Подключение к удаленной базе данных
url = 'https://alananisimov.github.io/test_web_db/test.db'
filename = 'test.db'

urllib.request.urlretrieve(url, filename)

conn = sqlite3.connect(filename)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activation_key_hash TEXT UNIQUE,
    expiration_date TEXT,
    role TEXT,
    email TEXT
)
""")
conn.commit()


@dp.message_handler(Command('start'))
async def start(message: Message):
    await bot.send_message(message.chat.id,
                           'Вот наше меню:',
                           reply_markup=keyboard)
    cursor.execute("INSERT INTO keys (user_id, role) VALUES (?, ?)",
                   (message.from_user.id, "user"))
    conn.commit()


PRICE = {
    '1': [LabeledPrice(label='Тестовый период', amount=10000)],
    '2': [LabeledPrice(label='Одна Неделя', amount=10000)],
    '3': [LabeledPrice(label='Две Недели', amount=10000)],
    '4': [LabeledPrice(label='Один Месяц', amount=10000)],
    '5': [LabeledPrice(label='Один Год', amount=50000)],
    '6': [LabeledPrice(label='Навсегда', amount=100000)]
}

ACT_TIME = {
    '1': [LabeledPrice(label='Тестовый период', amount=14)],
    '2': [LabeledPrice(label='Одна Неделя', amount=7)],
    '3': [LabeledPrice(label='Две Недели', amount=14)],
    '4': [LabeledPrice(label='Один Месяц', amount=30)],
    '5': [LabeledPrice(label='Один Год', amount=365)],
    '6': [LabeledPrice(label='Навсегда', amount=100000000)]

}


@dp.message_handler(Command("get_key"))
async def get_activation_key(message: aiogram.types.Message, nums_re1: int):
    us_id = message.from_user.id
    cursor.execute("SELECT role FROM keys WHERE user_id=?", (us_id,))
    result = cursor.fetchone()
    conn.commit()

    if result and result[0] == 'buyers':
        activation_key = str(uuid.uuid4())
        activation_key_hash = hashlib.md5(activation_key.encode()).hexdigest()

        # Устанавливаем срок действия ключа
        expiration_date = datetime.datetime.now() + datetime.timedelta(days=nums_re1)

        # Добавляем информацию о ключе в базу данных
        cursor.execute("UPDATE keys SET activation_key_hash = ?, expiration_date = ? WHERE user_id = ?",
                       (activation_key_hash, expiration_date.strftime('%Y-%m-%d %H:%M:%S'), message.from_user.id))
        conn.commit()

        # Отправляем пользователю новый ключ
        await message.answer(f'Ваш активационный ключ: {activation_key}')
    else:
        # Если нет роли buyers, то отправляем сообщение
        await message.answer("У вас нет прав для использования этой команды")


dp.register_message_handler(get_activation_key, commands=['get_key'])


# Обновляю роль: Принимает роль и id пользователя
async def update_user_role(user_id: int, new_role: str):
    cursor.execute("UPDATE keys SET role = ? WHERE user_id = ?", (new_role, user_id))
    conn.commit()


@dp.message_handler(content_types='web_app_data')
async def buy_process(web_app_message):
    await bot.send_invoice(web_app_message.chat.id,
                           title='Покупка',
                           description='Заоблачный фпс, за минимальные вложения',
                           provider_token="381764678:TEST:53188",
                           currency='rub',
                           need_email=True,
                           photo_url="https://alananisimov.github.io/webapp/buy.png",
                           need_phone_number=True,
                           prices=PRICE[f'{web_app_message.web_app_data.data}'],
                           start_parameter='example',
                           payload=ACT_TIME[f'{web_app_message.web_app_data.data}'])


@dp.pre_checkout_query_handler(lambda q: True)
async def checkout_process(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    duration = pre_checkout_query.invoice_payload.

@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: Message):
    await bot.send_message(message.chat.id,
                           'Оплата успешно отправлена',
                           reply_markup=keyboard)
    user_id = message.from_user.id
    order_info = message.successful_payment.invoice_payload
    e_mail = message.successful_payment.order_info.email
    await bot.send_message(message.chat.id, f"Используйте email для идентификации: {e_mail}")
    await bot.send_message(message.chat.id, f"Время действия подписки:")
    cursor.execute("UPDATE keys SET email = ? WHERE user_id = ?",
                   (e_mail, message.from_user.id))
    nums = re.findall(r'\d+', order_info)

    nums = [int(i) for i in nums]

    nums_re1 = int(nums_re)
    print(nums_re1)

    conn.commit()
    new_role = "buyers"
    # Вызываем метод update_user_role чтобы обновить роль пользователя
    await update_user_role(user_id, new_role)
    await get_activation_key(nums_re1)
