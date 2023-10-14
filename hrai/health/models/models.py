# models.py (в вашем Django-приложении)

from django.db import models

class JsonModel(models.Model):
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.city}'

# Создайте миграции для этой модели:
# python manage.py makemigrations ваше_приложение

# Примените миграции:
# python manage.py migrate ваше_приложение
