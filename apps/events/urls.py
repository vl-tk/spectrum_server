from apps.events.views import EventListView, EventUpdateView
from django.urls import path
from rest_framework import routers

app_name = 'Events API'

router = routers.SimpleRouter()

urlpatterns = [
    path('', EventListView.as_view(), name='list_events'),
    path('<int:id>', EventUpdateView.as_view(), name='update_event')
]

urlpatterns += router.urls
