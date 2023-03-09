from apps.report.views import (CHZRecordCityFilterView, CHZRecordGTINView,
                               CHZRecordINNView, CHZRecordPositionsFilterView,
                               CHZRecordProductNameFilterView,
                               CHZRecordRegionFilterView, CHZReport1View,
                               CHZReport2View, CHZReport3View, CHZReport4View,
                               CHZReport5View, CHZReport6View, CHZReport7View)
from django.urls import path
from rest_framework import routers

app_name = 'Clients API'

router = routers.SimpleRouter()

urlpatterns = [
    # reports filter helpers (from app.data data)
    path('helper/regions', CHZRecordRegionFilterView.as_view(), name='chz_report_filter_regions'),
    path('helper/cities', CHZRecordCityFilterView.as_view(), name='chz_report_filter_cities'),
    path('helper/gtin_list', CHZRecordGTINView.as_view(), name='chz_report_gtin'),
    path('helper/inn_list', CHZRecordINNView.as_view(), name='chz_report_inn'),
    path('helper/products', CHZRecordProductNameFilterView.as_view(), name='chz_products'),
    path('helper/positions', CHZRecordPositionsFilterView.as_view(), name='chz_positions'),
    # reports
    path('custom/retail_sales_for_inn', CHZReport1View.as_view(), name='chz_report1'),
    path('custom/retail_sales_for_gtin', CHZReport2View.as_view(), name='chz_report2'),
    path('custom/wholesale_sales', CHZReport3View.as_view(), name='chz_report3'),
    path('custom/wholesale_sales_for_gtin', CHZReport4View.as_view(), name='chz_report4'),
    path('custom/dynamics_of_retail_sales', CHZReport5View.as_view(), name='chz_report5'),
    path('custom/abc_per_regions', CHZReport6View.as_view(), name='chz_report6'),
    path('custom/universes_list', CHZReport7View.as_view(), name='chz_report7')
]

urlpatterns += router.urls
