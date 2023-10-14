import overpy
import math
import threading
import time
# Словарь с рейтингами объектов
ratings = {
    "e-cigarette": -40,
    "tobacco": -90,
    "bar": -60,
    "biergarten": -50,
    "pub": -50,
    "wine": -30,
    "alcohol": -80,
    "beverages": -70,
    "fast_food": -90,
    "food_court": -80,
    "swimming pool": 90,
    "stadium": 80,
    "manege": 75,
    "fitness club": 85,
    "gym": 70,
    "bike path": 75,
    "skating rinks": 75,
    "ice fields for skating": 75,
    "Parks": 80,
    "open. green area for recreation": 85,
    "pedestrian paths": 70,
    "sidewalks": 60,
    "sports ground": 75,
    "football fields": 80,
    "sports center": 85,
    "large stadiums": 70,
    "jogging paths": 70,
    "bicycle paths": 75,
    "equestrian tracks": 80,
    "market": 65,
    "bazaar": 60,
    "fresh fruit and vegetable stores": 85,
    "farm shops": 85
}

# Функция для пересчета рейтинга в новый диапазон (1-100)
def rescale_rating(old_rating):
    old_min = -90
    old_max = 90
    new_min = 1
    new_max = 100
    return (old_rating - old_min) / (old_max - old_min) * (new_max - new_min) + new_min

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
          node["amenity"="school"](area.district);
          node["amenity"="university"](area.district);
          node["amenity"="college"](area.district);
          node["amenity"="kindergarten"](area.district);
          node["amenity"="music_school"](area.district);
          node["amenity"="technical school"](area.district);
          node["amenity"="vocational lyceum"](area.district);
          node["amenity"="secondary educational institution"](area.district);
          node["amenity"="primary school"](area.district);
          node["amenity"="secondary school"](area.district);
          node["amenity"="gymnasium"](area.district);
          node["amenity"="lyceum"](area.district);
          node["amenity"="language school"](area.district);
          node["amenity"="music school"](area.district);
        );
        out;
        """
        result_education = api.query(query_education)
        education_count = len(result_education.nodes)

        # Запросы для негативно влияющих и позитивно влияющих объектов в районе
        query_unhealthy = f"""
        area[name="{district_name}"]->.district;
        (
          node["shop"="tobacco"](area.district);
          node["shop"="alcohol"](area.district);
          node["shop"="fast_food"](area.district);
          node["shop"="jewelry"](area.district);
          node["shop"="weapons"](area.district);
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

        query_positive = f"""
        area[name="{district_name}"]->.district;
        (
          node["amenity"="park"](area.district);
          node["amenity"="library"](area.district);
          node["amenity"="theatre"](area.district);
          node["amenity"="museum"](area.district);
        );
        out;
        """
        result_positive = api.query(query_positive)
        positive_count = len(result_positive.nodes)

        # Создаем словарь для подсчета количества объектов для каждого тега
        tag_counts = {}

        # Считаем объекты для тегов, негативно влияющих на район
        for node in result_unhealthy.nodes:
            node_tag = node.tags.get("shop", "")
            if node_tag in ratings:
                if node_tag in tag_counts:
                    tag_counts[node_tag] += 1
                else:
                    tag_counts[node_tag] = 1

        # Считаем объекты для тегов, позитивно влияющих на район
        for node in result_positive.nodes:
            node_tag = node.tags.get("amenity", "")
            if node_tag in ratings:
                if node_tag in tag_counts:
                    tag_counts[node_tag] += 1
                else:
                    tag_counts[node_tag] = 1

        # Вычисляем рейтинг района как отношение положительных к отрицательным объектам и пересчитываем его
        if unhealthy_count >= 0:
            district_rating = (positive_count / (unhealthy_count + positive_count)) * 100
        # else:
        #     district_rating = 0

        # Выводим информацию о районе и его рейтинге
        analysis = {'district': district_name,
               'educations' : education_count,
               'unhealthy' : unhealthy_count,
               'positive' : positive_count,
               'rating' : district_rating,
               }
        return analysis, tag_counts


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

    # Если районов с admin_level=9 нет, используйте admin_level=8
    if not result_districts_9.relations:
        query_districts_8 = f"""
        area[name="{city_name}"]->.city;
        (
        relation(area.city)["boundary"="administrative"]["admin_level"="8"];
        );
        out;
        """
        result_districts = api.query(query_districts_8)
    else:
        result_districts = result_districts_9

    # Создайте список потоков для обработки районов
    threads = []
    for rel in result_districts.relations:
        thread = threading.Thread(target=process_district, args=(rel, api))
        threads.append(thread)
        thread.start()
        time.sleep(0.7)

    for thread in threads:
        thread.join()