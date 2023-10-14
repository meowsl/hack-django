from django.shortcuts import render
import requests
from .models.models import JsonModel
import os, json
from rest_framework import viewsets
from .models.models import JsonModel
from .serializers import JsonModelSerializer

class JsonModelViewSet(viewsets.ModelViewSet):
    queryset = JsonModel.objects.all()
    serializer_class = JsonModelSerializer

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

# Функция для загрузки данных из JSON в модель Django
def load_data_from_json():
    with open('health/cities.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Создайте объекты модели Django на основе данных из JSON
    for item in data:
        region = item['region']
        city = item['city']

        JsonModel.objects.create(region=region, city=city)

# Функция для отображения страницы
def indexpage(request):
    # Вызов функции для загрузки данных из JSON в модель Django
    load_data_from_json()

    cities = get_russian_cities()

    return render(request, 'index.html', {'list_cities' : cities})
