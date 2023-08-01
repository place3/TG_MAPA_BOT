from aiogram import Dispatcher, Bot, types, executor
from aiogram.types import MediaGroup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from AIGRAM_TOKEN import AIOGRAM__TOKEN
from Parser import get_coordinates, get_distance, get_image, get_attractionss, get_weather
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = AIOGRAM__TOKEN
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


def on_startup(_):
    print('ПОЕХАЛИ!')


async def set_default_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("cancel", "остановить бота"),
        types.BotCommand("description", 'описание'),
    ])


class FindLocReg(StatesGroup):
    waiting_for_city = State()
    waiting_for_command = State()
    waiting_for_loc = State()
    waiting_for_find_loc = State()

data_city = ''

description = '''Привет! Добро пожаловать в наш Бот-путеводитель!

Наш бот создан для того, чтобы сделать вашу жизнь проще и приятнее. Вот некоторые из основных функций, которыми вы можете воспользоваться:

Калькулятор расстояний: Наш бот может быстро рассчитать расстояние между вашим текущим местоположением и любой другой точкой на карте. Это может быть невероятно полезно при планировании поездок или просто для того, чтобы лучше ориентироваться в окружающей обстановке.

Прогнозы погоды: Хотите узнать погоду в конкретном городе? Наш бот может помочь! Просто введите название города, и мы предоставим вам актуальную информацию о погоде.

Развлекательные места: Если вы ищете, чем заняться, наш бот предложит вам интересные и увлекательные места. Если вы находитесь в новом городе или просто хотите исследовать свой родной город, мы поможем вам найти что-то новое и интересное.
'''

@dp.message_handler(commands='description', state='*')
async def desc(msg: types.Message, state: FSMContext):
    await msg.answer(description, )

@dp.message_handler(commands='start', state='*')
async def st_hi(msg: types.Message, state: FSMContext):
    await set_default_commands(bot)
    await msg.answer(text='''
Привет!
Я бот путеводитель, и я постараюсь тебе помочь :)
Чтобы начать, просто напиши мне город, в котором ты находишься''')
    await state.set_state(FindLocReg.waiting_for_city.state)


@dp.message_handler(content_types=['text'], state=FindLocReg.waiting_for_city)
async def choose_city(msg: types.Message, state: FSMContext):
    global data_city
    data_city = str(msg.text.capitalize())
    await state.update_data(city=msg.text.capitalize())
    await state.set_state(FindLocReg.waiting_for_command.state)
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/get_distance')).insert(KeyboardButton('/weather')).add(KeyboardButton('/attractions'))
    await msg.answer(text='''
Супер!
Наш бот легко посчитает расстояние от тебя до любой точки!
Определит погоду в твоём городе.
А главное, поможет провести время в интересных местах!
''', reply_markup=kb)


@dp.message_handler(commands=['weather'], state='*')
async def get_weatherr(msg: types.message):
    cords = get_coordinates(data_city)
    res = get_weather(cords)
    await msg.answer(f"{res}", reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['attractions'], state='*')
async def get_attractions(msg: types.Message):
    attr = get_attractionss(data_city)
    names = [a[2] for a in attr]
    cords = [get_coordinates(a) for a in names]
    if attr == 'Извините в нашей базе данных нету информации по данному городу:(':
        msg.answer('Извините в нашей базе данных нету информации по данному городу:(')
    for n in range(3):
        await bot.send_photo(chat_id=msg.from_user.id, photo=attr[n][1], caption=attr[n][0])
        await bot.send_location(chat_id=msg.from_user.id, longitude=cords[n][1], latitude=cords[n][0])

@dp.message_handler(commands=['get_distance'], state=FindLocReg.waiting_for_command)
async def choose_city(msg: types.Message, state: FSMContext):
    await msg.answer(text='Теперь, отправь мне свою геопозицию', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FindLocReg.waiting_for_loc.state)


@dp.message_handler(content_types=types.ContentType.LOCATION, state=FindLocReg.waiting_for_loc)
async def get_loca(msg: types.Message, state: FSMContext):
    latitude = msg.location.latitude
    longitude = msg.location.longitude
    cords_1 = (latitude, longitude)
    await state.update_data(loca=cords_1)
    await state.set_state(FindLocReg.waiting_for_find_loc.state)
    await msg.answer(text='А теперь, напиши искомую точку')


@dp.message_handler(content_types=['text'], state=FindLocReg.waiting_for_find_loc)
async def get_find_loc(msg: types.Message, state: FSMContext):
    local_user_datas = await state.get_data()
    cord_1 = local_user_datas['loca']
    cord_2 = get_coordinates(f'{local_user_datas["city"]} {msg.text}')
    distance_for = get_distance(cord_1, cord_2)
    get_image(f'{local_user_datas["city"]} {msg.text}')
    album = MediaGroup()
    album.attach_photo(
        types.InputFile(rf'C:\Users\1\Desktop\TG_BOT\photo\{local_user_datas["city"]} {msg.text}\000001.jpg'))
    album.attach_photo(
        types.InputFile(rf'C:\Users\1\Desktop\TG_BOT\photo\{local_user_datas["city"]} {msg.text}\000002.jpg'),
        caption=f'{distance_for} до {msg.text}')
    await msg.answer_media_group(media=album)
    await state.finish()


@dp.message_handler(commands='cancel', state='*')
async def breaking(msg: types.Message, state: FSMContext):
    await msg.answer(text='Действие отменено')
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
