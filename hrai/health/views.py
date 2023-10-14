from django.shortcuts import render
import requests

# Функция для получения всех Российских городов
def get_russian_cities():
    # Данные для запроса
    overpass_query = """
    [out:json];
    area[name="Россия"]->.a;
    (
      node["place"="city"](area.a);
      way["place"="city"](area.a);
      relation["place"="city"](area.a);
    );
    out center;
    """
    # Url api для запроса
    overpass_url = "https://overpass-api.de/api/interpreter"
    # Запрос
    response = requests.get(overpass_url, params={'data': overpass_query})
    # Проверка кода ответа & создание массива городов
    if response.status_code == 200:
        data = response.json()
        cities = set()

        for element in data['elements']:
            if 'name' in element['tags']:
                cities.add(element['tags']['name'])

        return list(cities)

# Функция для отображения страницы
def indexpage(request):

    cities = get_russian_cities()

    return render(request, 'index.html', {'list_cities' : cities})