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
list_analysis =[]
list_recomends = []
recomend = {}

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

# Создайте словарь с выбранными положительными тегами
positive_tags = {
    "park",
    "library",
    "theatre",
    "museum",
    "swimming pool",
    "stadium",
    "manege",
    "fitness club",
    "gym",
    "bike path",
    "skating rinks",
    "ice fields for skating",
    "parks",
    "green area for recreation",
    "pedestrian paths",
    "sidewalks",
    "sports ground",
    "football fields",
    "sports center",
    "large stadiums",
    "jogging paths",
    "bicycle paths",
    "equestrian tracks",
    "market",
    "bazaar",
    "fresh fruit and vegetable stores",
    "farm shops"
}

# Создайте словарь с рейтингами тегов
tag_ratings = {
    "park": 90,
    "library": 85,
    "theatre": 85,
    "museum": 85,
    "swimming pool": 85,
    "stadium": 85,
    "manege": 80,
    "fitness club": 80,
    "gym": 80,
    "bike path": 80,
    "skating rinks": 75,
    "ice fields for skating": 75,
    "parks": 75,
    "green area for recreation": 75,
    "pedestrian paths": 70,
    "sidewalks": 70,
    "sports ground": 70,
    "football fields": 70,
    "sports center": 70,
    "large stadiums": 70,
    "jogging paths": 70,
    "bicycle paths": 70,
    "equestrian tracks": 70,
    "market": 65,
    "bazaar": 60,
    "fresh fruit and vegetable stores": 60,
    "farm shops": 60
}

# В цикле для обработки районов
def process_district(rel, api):
    tag_counts_positive = {}
    tag_counts_negative = {}

    if "name" in rel.tags:
        district_name = rel.tags["name"]

        # Query for educational institutions
        query_education = f"""
        area[name="{district_name}"]->.district;
        (
          node["amenity"="school"](area.district);
          node["education"="school"](area.district);
          node["building"="school"](area.district);
          node["education"="university"](area.district);
          node["amenity"="university"](area.district);
          node["building"="university"](area.district);
          node["amenity"="college"](area.district);
          node["building"="college"](area.district);
          node["education"="college"](area.district);
          node["amenity"="kindergarten"](area.district);
          node["building"="kindergarten"](area.district);
          node["education"="kindergarten"](area.district);
          node["amenity"="music_school"](area.district);
          node["building"="music_school"](area.district);
          node["education"="music_school"](area.district);
          node["amenity"="technical school"](area.district);
          node["building"="technical school"](area.district);
          node["education"="technical school"](area.district);
          node["amenity"="vocational lyceum"](area.district);
          node["building"="vocational lyceum"](area.district);
          node["education"="vocational lyceum"](area.district);
          node["amenity"="secondary educational institution"](area.district);
          node["building"="secondary educational institution"](area.district);
          node["amenity"="secondary educational institution"](area.district);
          node["building"="primary school"](area.district);
          node["amenity"="primary school"](area.district);
          node["education"="primary school"](area.district);
          node["amenity"="secondary school"](area.district);
          node["building"="secondary school"](area.district);
          node["education"="secondary school"](area.district);
          node["amenity"="gymnasium"](area.district);
          node["building"="gymnasium"](area.district);
          node["education"="gymnasium"](area.district);
          node["amenity"="lyceum"](area.district);
          node["building"="lyceum"](area.district);
          node["education"="lyceum"](area.district);
          node["amenity"="language school"](area.district);
          node["building"="language school"](area.district);
          node["education"="language school"](area.district);
          node["amenity"="music school"](area.district);
          node["building"="music school"](area.district);
          node["education"="music school"](area.district);
        );
        out;
        """
        result_education = api.query(query_education)
        education_count = len(result_education.nodes)

        # Query for positive objects
        query_positive = f"""
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
          node["shop"](area.district);
        );
        out;
        """
        result_positive = api.query(query_positive)
        positive_count = len(result_positive.nodes)

        # Query for negative objects
        query_negative = f"""
            area[name="{district_name}"]->.district;
            (
            node["shop"="alcohol"](area.district);
            node["building"="alcohol"](area.district);
            node["shop"="fast_food"](area.district);
            node["building"="fast_food"](area.district);
            node["shop"="e-cigarette"](area.district);
            node["building"="e-cigarette"](area.district);
            node["shop"="biergarten"](area.district);
            node["building"="biergarten"](area.district);
            node["shop"="pub"](area.district);
            node["building"="pub"](area.district);
            node["shop"="wine"](area.district);
            node["building"="wine"](area.district);
            node["shop"="beverages"](area.district);
            node["building"="beverages"](area.district);
            node["shop"="food_court"](area.district);
            node["building"="food_court"](area.district);
            );
            out;
        """
        result_negative = api.query(query_negative)
        negative_count = len(result_negative.nodes)

        # Get the coordinates of educational institutions
        education_coords = [(node.lat, node.lon) for node in result_education.nodes]
        # Calculate distances to positive objects
        for node in result_positive.nodes:
            lat = node.lat
            lon = node.lon

            for edu_lat, edu_lon in education_coords:
                distance = haversine(lat, lon, edu_lat, edu_lon)
                if distance <= 0.20:  # Check if the distance is within 250 meters (0.25 kilometers)
                    node_tag = node.tags.get("leisure", "") or node.tags.get("amenity", "") or node.tags.get("shop", "")
                    if node_tag in positive_tags:
                        if node_tag in tag_counts_positive:
                            tag_counts_positive[node_tag] += 1
                        else:
                            tag_counts_positive[node_tag] = 1

                # Calculate distances to negative objects
        for node in result_negative.nodes:
            lat = node.lat
            lon = node.lon

            for edu_lat, edu_lon in education_coords:
                distance = haversine(lat, lon, edu_lat, edu_lon)
                if distance <= 0.20:  # Check if the distance is within 250 meters (0.25 kilometers)
                    # Object is within the specified radius
                    node_tag = node.tags.get("amenity", "") or node.tags.get("shop", "") or node.tags.get("leisure", "") or node.tags.get("building", "")
                    if node_tag in ratings:
                        if node_tag in tag_counts_negative:
                            tag_counts_negative[node_tag] += 1
                        else:
                            tag_counts_negative[node_tag] = 1

        # Calculate the district rating
        district_rating = calculate_district_rating(positive_count, negative_count)

        # Print the information about the district
        analysis = {'district': district_name,
                    'educations': education_count,
                    'unhealthy': negative_count,
                    'positive': positive_count,
                    'rating': district_rating,
                    }
        analysis.update(tag_counts_negative)
        analysis.update(tag_counts_positive)
        analysis['ecigarette'] = analysis.pop('e-cigarette')
        list_analysis.append(analysis)
        if "tabaco" in tag_counts_negative and tag_counts_negative["tabaco"] >= 3:

            recomend = {1: 'Регулировать продажу табачных изделий вблизи образовательных учреждений.',
                        2:'Популяризировать кампании по борьбе со вредными привычками.' }

        elif "library" in tag_counts_positive and tag_counts_positive["library"] >= 2:

            recomend = {1: 'Поддерживать и расширять сеть библиотек в районе для повышения образованности.',
                        2: 'Организовать культурные и образовательные мероприятия в библиотеках.'}

        elif "alcohol" in tag_counts_negative and tag_counts_negative["alcohol"] >= 2:

            recomend = {1: 'Регулировать продажу алкоголя и баров вблизи образовательных учреждений.',
                        2: 'Поддерживать программы по профилактике алкогольных зависимостей.'}

        else:

            recomend = {1: 'Усилить образовательную инфраструктуру, расширив количество и качество учебных заведений.',
                        2: 'Развивать зеленые зоны и парки для отдыха и рекреации жителей.',
                        3: 'Поддерживать спортивные клубы и секции для активизации жизни в районе.'}

    elif "wine" in tag_counts_negative and tag_counts_negative["wine"] >= 2:
        print("1. Ограничить продажу алкогольных напитков в районе.")
        print("2. Развивать мероприятия, направленные на борьбу с алкогольной зависимостью.")
        recomend = {1: 'Ограничить продажу алкогольных напитков в районе.',
                    2: 'Развивать мероприятия, направленные на борьбу с алкогольной зависимостью.'}

    elif "park" in tag_counts_positive and tag_counts_positive["park"] >= 2:

        recomend = {1: 'Усилить уход и развитие парков и зеленых зон.',
                    2: 'Организовать культурные события и мероприятия в парках.'}

    elif "e-cigarette" in tag_counts_negative and tag_counts_negative["e-cigarette"] >= 2:
        recomend = {1: 'Регулировать продажу электронных сигарет и продуктов вблизи образовательных учреждений.',
                    2: 'Проводить просветительскую работу по вреду электронного курения.'}

    elif "beverages" in tag_counts_negative and tag_counts_negative["beverages"] >= 3:
        recomend = {1: 'Ограничить продажу напитков с высоким содержанием сахара в районе.',
                    2: 'Популяризировать здоровое питание и напитки с низким содержанием сахара.'}


    else:
        recomend = {1: 'Усилить образовательную инфраструктуру, расширив количество и качество учебных заведений.',
                    2: 'Развивать зеленые зоны и парки для отдыха и рекреации жителей.',
                    3: 'Поддерживать спортивные клубы и секции для активизации жизни в районе.'}



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

# Функция для вычисления рейтинга района
def calculate_district_rating(positive_count, negative_count):
    if negative_count >= 0:
        rating = (positive_count / (positive_count + negative_count)) * 100
        return rating
    else:
        return 0


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
        time.sleep(0.3)

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
    list_recomends.clear()
    if request.method == "POST":
        choose_city = request.POST['city']
        return resultspage(request, choose_city)

    citi = get_self_api()

    return render(request, 'index.html', {'list_cities' : citi})

def resultspage(request, city):
    get_info(city)
    anal = list_analysis
    recs = recomend
    return render(request, 'results.html', {'list_analysis' : anal, 'city' : city, 'recomends' : recs})

