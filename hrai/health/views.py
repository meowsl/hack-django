from django.shortcuts import render, redirect
import requests, time, overpy, math, threading
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

# Словарь с рейтингами объектов
ratings = {
    "swimming pool": 90,
    "open. green area for recreation": 85,
    "fresh fruit and vegetable stores": 85,
    "farm shops": 85,
    "fitness club": 85,
    "sports center": 85,
    "equestrian tracks": 80,
    "stadium": 80,
    "parks": 80,
    "football fields": 80,
    "manege": 75,
    "bike path": 75,
    "skating rinks": 75,
    "ice fields for skating": 75,
    "sports ground": 75,
    "pedestrian paths": 70,
    "gym": 70,
    "jogging paths": 70,
    "large stadiums": 70,
    "bicycle paths": 75,
    "market": 65,
    "bazaar": 60,
    "sidewalks": 60,
    "wine": -30,
    "bar": -60,
    "pub": -50,
    "biergarten": -50,
    "beverages": -70,
    "wine": -30,
    "alcohol": -80,
    "tobacco": -90,
    "fast_food": -90,
    "food_court": -80,
    "e-cigarette": -40,
    "weapons": -100,
    "jewelry": -10
}

list_analysis = []

sorted_ratings = dict(sorted(ratings.items(), key=lambda x: x[1], reverse=True))

def calculate_district_rating(positive_count, unhealthy_count):
    if unhealthy_count >= 0:
        rating = (positive_count / (positive_count + unhealthy_count)) * 100
        return rating
    else:
        return 0

# Функция для вычисления расстояния между двумя точками (широта и долгота) на поверхности Земли
def haversine(lat1, lon1, lat2, lon2):
    # Радиус Земли в километрах
    R = 6371.0

    # Перевести угловые координаты из градусов в радианы
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Разница между широтами и разница между долготами
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Формула гаверсинуса
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Расстояние между двумя точками
    distance = R * c

    return distance
# Функция для обработки района
def process_district(rel, api):
    if "name" in rel.tags:
        district_name = rel.tags["name"]

        # Здесь можно добавить искусственную задержку, если количество районов больше 8

        # Запросы и обработка результатов как раньше
        query_education = f"""
        area[name="{district_name}"]->.district;
        (
          node["education"="school"](area.district);
          node["education"="university"](area.district);
          node["education"="college"](area.district);
          node["education"="kindergarten"](area.district);
          node["education"="music_school"](area.district);
          node["education"="technical school"](area.district);
          node["education"="vocational lyceum"](area.district);
          node["education"="secondary educational institution"](area.district);
          node["education"="primary school"](area.district);
          node["education"="secondary school"](area.district);
          node["education"="gymnasium"](area.district);
          node["education"="lyceum"](area.district);
          node["education"="language school"](area.district);
          node["education"="music school"](area.district);
        );
        out;
        """
        result_education = api.query(query_education)
        education_count = len(result_education.nodes)
        positive_ratings = f"""
        area[name="{district_name}"]->.district;
        (
          node["leisure"="park"](area.district);
          node["amenity"="library"](area.district);
          node["amenity"="theatre"](area.district);
          node["amenity"="museum"](area.district);
          node["amenity"="swimming pool"](area.district);
          node["amenity"="stadium"](area.district);
          node["leisure"="manege"](area.district);
          node["leisure"="fitness club"](area.district);
          node["leisure"="gym"](area.district);
          node["leisure"="bike path"](area.district);
          node["leisure"="skating rinks"](area.district);
          node["leisure"="ice fields for skating"](area.district);
          node["leisure"="parks"](area.district);
          node["leisure"="green area for recreation"](area.district);
          node["leisure"="pedestrian paths"](area.district);
          node["leisure"="sidewalks"](area.district);
          node["leisure"="sports ground"](area.district);
          node["leisure"="football fields"](area.district);
          node["leisure"="sports center"](area.district);
          node["leisure"="large stadiums"](area.district);
          node["leisure"="jogging paths"](area.district);
          node["leisure"="bicycle paths"](area.district);
          node["leisure"="equestrian tracks"](area.district);
          node["shop"="market"](area.district);
          node["shop"="bazaar"](area.district);
          node["shop"="fresh fruit and vegetable stores"](area.district);
          node["shop"="farm shops"](area.district);
        );
        out;
        """
        result_positive = api.query(positive_ratings)
        positive_count = len(result_positive.nodes)
        # Запросы для негативно влияющих и позитивно влияющих объектов в районе
        query_unhealthy = f"""
        area[name="{district_name}"]->.district;
        (
          node["shop"="tobacco"](area.district);
          node["shop"="alcohol"](area.district);
          node["shop"="fast_food"](area.district);
          node["shop"="e-cigarette"](area.district);
          node["shop"="biergarten"](area.district);
          node["shop"="pub"](area.district);
          node["shop"="wine"](area.district);
          node["shop"="beverages"](area.district);
          node["shop"="food_court"](area.district);
        );
        out;
        """
        result_unhealthy = api.query(query_unhealthy)
        unhealthy_count = len(result_unhealthy.nodes)

        # Создаем словарь для подсчета количества объектов для каждого тега
        tag_counts_positive = {}
        tag_counts_negative = {}
        # Для негативных тегов

        for node in result_unhealthy.nodes:
            node_tag = node.tags.get("shop", "")
            if node_tag in ratings:
                if node_tag in tag_counts_negative:
                    tag_counts_negative[node_tag] += 1
                else:
                    tag_counts_negative[node_tag] = 1

        # Для положительных тегов
        for node in result_positive.nodes:
            node_tag = node.tags.get("amenity", "") or node.tags.get("shop", "") or node.tags.get("leisure", "")
            if node_tag in positive_ratings:
                if node_tag in tag_counts_positive:
                    tag_counts_positive[node_tag] += 1
                else:
                    tag_counts_positive[node_tag] = 1

        # Выводим информацию о районе и его рейтинге
        district_rating = calculate_district_rating(positive_count, unhealthy_count)

        analysis = {'district': district_name,
                    'educations': education_count,
                    'unhealthy': unhealthy_count,
                    'positive': positive_count,
                    'rating': district_rating,
                    }
        analysis.update(tag_counts_negative)
        analysis.update(tag_counts_positive)
        analysis['ecigarette'] = analysis.pop('e-cigarette')
        list_analysis.append(analysis)


def get_info(city_name):
    # Создайте объект Overpass API
    api = overpy.Overpass()

    # Запрос для получения границ районов города (admin_level 9)
    query_districts_9 = f"""
    area[name="{city_name}"]->.city;
    (
      relation(area.city)["boundary"="administrative"]["admin_level"="9"];
    );
    out;
    """

    # Выполните запрос для районов с admin_level=9
    result_districts_9 = api.query(query_districts_9)

    # Запрос для получения границ районов города (admin_level 8)
    query_districts_8 = f"""
    area[name="{city_name}"]->.city;
    (
      relation(area.city)["boundary"="administrative"]["admin_level"="8"];
    );
    out;
    """

    # Выполните запрос для районов с admin_level=8
    result_districts_8 = api.query(query_districts_8)

    # Используйте результат с наивысшим доступным уровнем (9, если 8 тоже есть)
    if result_districts_9.relations:
        result_districts = result_districts_9
    elif result_districts_8.relations:
        result_districts = result_districts_8
    else:
        query_city = f"""
        area[name="{city_name}"]->.city;
        (
        relation(area.city)["admin_level"];
        );
        out;
        """
        result_city = api.query(query_city)
        result_districts = result_city

    # Создайте список потоков для обработки районов
    threads = []
    for rel in result_districts.relations:
        thread = threading.Thread(target=process_district, args=(rel, api))
        threads.append(thread)
        thread.start()
        time.sleep(0.8)

    for thread in threads:
        thread.join()

def get_self_api():
    cities = []
    response = requests.get('http://127.0.0.1:8000/api/jsonmodels/')
    data = response.json()
    for item in data:
        cities.append(item['city'])

    return cities

# Функция для отображения страницы
def indexpage(request):
    # Вызов функции для загрузки данных из JSON в модель Django
    list_analysis.clear()
    if request.method == "POST":
        choose_city = request.POST['city']
        return resultspage(request, choose_city)

    citi = get_self_api()

    return render(request, 'index.html', {'list_cities' : citi})

def resultspage(request, city):
    get_info(city)
    anal = list_analysis
    return render(request, 'results.html', {'list_analysis' : anal, 'city' : city})

