from apps.data.views import CHZListView, DGisRecordListView
# from apps.users.views import ClientListView, ClientRetrieveView
from django.urls import path
from rest_framework import routers

app_name = 'Clients API'

router = routers.SimpleRouter()

urlpatterns = [
    # path('', ClientListView.as_view(), name='list_clients'),
    # path('<int:pk>', ClientRetrieveView.as_view(), name='retrieve_client'),
    path('chzrecords', CHZListView.as_view(), name='chz_records'),
    path('dgisrecords', DGisRecordListView.as_view(), name='dgis_records'),
]

urlpatterns += router.urls
