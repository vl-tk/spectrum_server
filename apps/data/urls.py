from apps.data.views import (CHZListView, DGisRecordListView,
                             DGisRecordPotentialListView)
from apps.data.views_reports import (CHZRecordGTINView,
                                     CHZRecordRegionFilterView, CHZReport1View)
from django.urls import path
from rest_framework import routers

app_name = 'Clients API'

router = routers.SimpleRouter()

urlpatterns = [
    # path('', ClientListView.as_view(), name='list_clients'),
    # path('<int:pk>', ClientRetrieveView.as_view(), name='retrieve_client'),
    path('chzrecords', CHZListView.as_view(), name='chz_records'),
    path('dgisrecords', DGisRecordListView.as_view(), name='dgis_records'),
    path('dgisrecords_potential', DGisRecordPotentialListView.as_view(), name='dgisrecords_potential'),
    path('reports/helper/regions', CHZRecordRegionFilterView.as_view(), name='chz_report_filter_regions'),
    path('reports/helper/gtin_list', CHZRecordGTINView.as_view(), name='chz_report_gtin'),
    path('reports/custom/retail_sales_for_gtin', CHZReport1View.as_view(), name='chz_report1')
]

urlpatterns += router.urls
