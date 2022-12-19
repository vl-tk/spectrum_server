from apps.log_app.views import LogListCreateView
from django.urls import path
from rest_framework import routers

app_name = 'Logs API'

router = routers.SimpleRouter()

urlpatterns = [
    path('', LogListCreateView.as_view(), name='list_events'),
]

urlpatterns += router.urls
