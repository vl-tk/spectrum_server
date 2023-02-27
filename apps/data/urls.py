from apps.data.views import (CHZListView, DGisRecordListView,
                             DGisRecordPotentialListView)
from apps.data.views_reports import (CHZRecordGTINView, CHZRecordINNView,
                                     CHZRecordPositionsFilterView,
                                     CHZRecordProductNameFilterView,
                                     CHZRecordRegionFilterView, CHZReport1View,
                                     CHZReport2View, CHZReport3View,
                                     CHZReport4View, CHZReport5View,
                                     CHZReport6View)
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
    # filter helpers
    path('reports/helper/regions', CHZRecordRegionFilterView.as_view(), name='chz_report_filter_regions'),
    path('reports/helper/gtin_list', CHZRecordGTINView.as_view(), name='chz_report_gtin'),
    path('reports/helper/inn_list', CHZRecordINNView.as_view(), name='chz_report_inn'),
    path('reports/helper/products', CHZRecordProductNameFilterView.as_view(), name='chz_products'),
    path('reports/helper/positions', CHZRecordPositionsFilterView.as_view(), name='chz_positions'),
    # graphs
    path('reports/custom/retail_sales_for_inn', CHZReport1View.as_view(), name='chz_report1'),
    path('reports/custom/retail_sales_for_gtin', CHZReport2View.as_view(), name='chz_report2'),
    path('reports/custom/wholesale_sales', CHZReport3View.as_view(), name='chz_report3'),
    path('reports/custom/wholesale_sales_for_gtin', CHZReport4View.as_view(), name='chz_report4'),
    path('reports/custom/dynamics_of_retail_sales', CHZReport5View.as_view(), name='chz_report5'),
    path('reports/custom/abc_per_regions', CHZReport6View.as_view(), name='chz_report6')
]

urlpatterns += router.urls
