from apps.events.views import (EventExportView, EventFilterView, EventListView,
                               EventMapGraphView, EventRegionGraphView,
                               EventReportView, EventStatsView,
                               EventSuggestionView, EventTypoCellsView,
                               EventTyposColumnView, EventUpdateView)
from django.urls import path
from rest_framework import routers

app_name = 'Events API'

router = routers.SimpleRouter()

urlpatterns = [
    path('', EventListView.as_view(), name='list_events'),
    path('<int:id>', EventUpdateView.as_view(), name='update_event'),
    path('export/', EventExportView.as_view(), name='export_events'),
    path('filters/', EventFilterView.as_view(), name='filter_events'),
    path('stats/', EventStatsView.as_view(), name='stats_events'),
    path('reports', EventReportView.as_view(), name='event_report'),
    path('graph/regions', EventRegionGraphView.as_view(), name='event_region_graph'),
    path('graph/map', EventMapGraphView.as_view(), name='event_map_graph'),
    path('suggestions', EventSuggestionView.as_view(), name='events_suggestions'),
    path('typos/columns', EventTyposColumnView.as_view(), name='events_typos_columns'),
    path('typos/cells', EventTypoCellsView.as_view(), name='events_typos_cells'),
]

urlpatterns += router.urls
