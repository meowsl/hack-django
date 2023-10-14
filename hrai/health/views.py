from django.shortcuts import render
import requests

def get_russian_cities():
    # Задайте ваш запрос Overpass. В этом примере мы ищем все объекты с тегом "place" равным "city" в России.
    overpass_query = """
    [out:json];
    area[name="Россия"]->.a;
    node["place"="city"](area.a);
    out center;
    """

    # URL Overpass API
    overpass_url = "https://overpass-api.de/api/interpreter"

    # Отправьте запрос Overpass
    response = requests.get(overpass_url, params={'data': overpass_query})

    if response.status_code == 200:
        data = response.json()
        cities = set()

        for element in data['elements']:
            if 'name' in element['tags']:
                cities.add(element['tags']['name'])

        return list(cities)

def indexpage(request):

    cities = get_russian_cities()

    return render(request, 'index.html', {'list_cities' : cities})