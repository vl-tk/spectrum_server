from django.urls import path
from rest_framework import routers

from apps.users.views import ClientListView, ClientRetrieveView

app_name = 'Clients API'

router = routers.SimpleRouter()

urlpatterns = [
    path('', ClientListView.as_view(), name='list_clients'),
    path('<int:pk>', ClientRetrieveView.as_view(), name='retrieve_client'),
]

urlpatterns += router.urls
