
from django.contrib import admin
from django.urls import path
from health.views import indexpage, resultspage
from django.urls import path, include
from rest_framework import routers
from health.views import JsonModelViewSet

router = routers.DefaultRouter()
router.register(r'jsonmodels', JsonModelViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('', indexpage),
    path('results/', resultspage)
]
