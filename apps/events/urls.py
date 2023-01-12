from apps.events.views import (EventExportView, EventFilterView, EventListView,
                               EventRegionGraphView, EventReportView,
                               EventUpdateView)
from django.urls import path
from rest_framework import routers

app_name = 'Events API'

router = routers.SimpleRouter()

urlpatterns = [
    path('', EventListView.as_view(), name='list_events'),
    path('<int:id>', EventUpdateView.as_view(), name='update_event'),
    path('export/', EventExportView.as_view(), name='export_events'),
    path('filters/', EventFilterView.as_view(), name='filter_events'),
    path('reports', EventReportView.as_view(), name='event_report'),
    path('graph/regions', EventRegionGraphView.as_view(), name='event_region_graph'),
]

urlpatterns += router.urls
