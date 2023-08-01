from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
from fake_useragent import UserAgent
from icrawler.builtin import GoogleImageCrawler
from bs4 import BeautifulSoup


def get_image(text):
    google_crawler = GoogleImageCrawler(storage={'root_dir': rf'C:\Users\1\Desktop\TG_BOT\photo\{text}'})
    google_crawler.crawl(keyword=f"{text}", max_num=2)


user = UserAgent().random
header = {
    'user-agent': user
}


def get_coordinates(address):
    loc = Nominatim(user_agent=UserAgent().random)
    get_loc = loc.geocode(address)
    return get_loc.latitude, get_loc.longitude


def get_distance(loc1, loc2):
    if geodesic(loc1, loc2).meters < 1000:
        return f'{round(geodesic(loc1, loc2).meters, 2)} м'
    return f'{round(geodesic(loc1, loc2).kilometers, 2)} км'

def get_attractionss(ur_city):
    of_sity = requests.get('https://wikiway.com/russia/goroda/', headers=header)
    of_sity.encoding = 'utf-8'
    src = of_sity.text
    page = BeautifulSoup(src, 'lxml')
    list_city_and_links = page.find('ul').find_all('a')
    list_city = [el.text for el in list_city_and_links]
    if ur_city.capitalize() not in list_city:
        return 'Извините в нашей базе данных нету информации по данному городу:('
    chosen_city = list(filter(lambda ell: True if ur_city.capitalize() in ell else False, list_city_and_links))[0]
    print(chosen_city)
    attractions_list = requests.get(f'https://wikiway.com/{chosen_city["href"]}dostoprimechatelnosti/', headers=header)
    attractions_list.encoding = 'utf-8'
    src1 = attractions_list.text
    page1 = BeautifulSoup(src1, 'lxml')
    list_of_attractions = page1.find('div', class_='wrap-list').find_all('a')
    list_of_attractions = [ek['href'] for ek in list_of_attractions]
    if len(list_of_attractions)>3:
        list_of_attractions = list_of_attractions[0:3]
    txt_list = []
    img_list = []
    name_list = []
    for attr in list_of_attractions:
        am = requests.get(f'https://wikiway.com/{attr}', headers=header)
        am.encoding = 'utf-8'
        src = am.text
        p_txt = BeautifulSoup(src, "lxml")
        txt_1 = p_txt.find('div', class_='element-anons').find('p').text
        txt_list.append(txt_1)
        img_1 = p_txt.find('div', class_='scroll').find('a')
        img_list.append(rf'https://wikiway.com/{img_1["href"]}')
        name_1 = p_txt.find('h1').text
        name_list.append(name_1)

    return list(zip(txt_list, img_list, name_list))

def get_weather(cords):
    api_key = "1ee9e1f690d70f0e1f698bc16e67667e"  # мой api ключ для openweather
    url = f'https://api.openweathermap.org/data/2.5/weather?lat={cords[0]}&lon={cords[1]}&appid={api_key}&units=metric'
    try:
        print('ff')

        data = requests.get(url).json()
        cur_temp = data['main']['temp']
        wind = data['wind']['speed']
        if int(wind) < 10:
            return f'температура на улице {cur_temp}°, ветер {wind} м/с'
        else:
            return f'температура на улице {cur_temp}°, осторожней, сильный ветер -  {wind} м/с'

    except:
        while not data:
            data = requests.get(url).json()
            cur_temp = data['main']['temp']
            wind = data['wind']['speed']
            if int(wind) < 10:
                return f'температура на улице {cur_temp}°, ветер {wind} м/с'
            else:
                return f'температура на улице {cur_temp}°, осторожней, сильный ветер -  {wind} м/с'
