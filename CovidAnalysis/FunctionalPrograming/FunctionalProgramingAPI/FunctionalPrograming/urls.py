from django.contrib import admin
from django.urls import path, include

from rest_framework import routers
from Covid.views import Covid

router = routers.DefaultRouter()
router.register('Covid', Covid, basename='Covid')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include((router.urls, 'Covid'), namespace='Covid')),
]

for url in router.urls:
    print(url)

