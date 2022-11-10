from apps.importer.views import ImportExcelView
from django.urls import path
from rest_framework import routers

app_name = 'Importer API'

router = routers.SimpleRouter()

urlpatterns = [
    path('', ImportExcelView.as_view(), name='import_file'),
]

urlpatterns += router.urls
