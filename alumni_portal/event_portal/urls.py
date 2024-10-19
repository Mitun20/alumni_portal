from django.urls import path
from .views import *

urlpatterns = [
    path('create_event_category/', CreateEventCategory.as_view(), name='create_event_category'),
    path('retrieve_event_category/', RetrieveEventCategory.as_view(), name='retrieve_event_category'),
    path('create_event/', CreateEvent.as_view(), name='create_event'),
    path('retrieve_event/', RetrieveEvent.as_view(), name='retrieve_event'),
    path('update_event/<int:event_id>/', UpdateEvent.as_view(), name='update_event'),
]
