from django.urls import path
from .views import *

urlpatterns = [
    
    # Category
    path('create_event_category/', CreateEventCategory.as_view(), name='create_event_category'),
    path('retrieve_event_category/', RetrieveEventCategory.as_view(), name='retrieve_event_category'),
    path('update_event_category/<int:category_id>/', UpdateEventCategory.as_view(), name='update_event_category'),
    
    # Event 
    path('create_event/', CreateEvent.as_view(), name='create_event'),
    path('retrieve_event/', RetrieveEvent.as_view(), name='retrieve_event'),
    path('update_event/<int:event_id>/', UpdateEvent.as_view(), name='update_event'),
    path('inactive_event/<int:event_id>/', DeactivateEvent.as_view(), name='inactive_event'),
    path('active_event/', ActiveEvent.as_view(), name='active_event'),
    path('event_by_category/<int:category_id>/', EventByCategory.as_view(), name='event_by_category'),
    
    # Question
    path('create_question/', CreateQuestion.as_view(), name='create_question'),
    path('create_event_question/<int:event_id>/', CreateEventQuestion.as_view(), name='create_event_question'),
    path('retrieve_question/<int:question_id>/', RetrieveQuestion.as_view(), name='retrieve_question'),
    path('update_question/<int:question_id>/', UpdateQuestion.as_view(), name='update_question'),
    path('delete_question/<int:question_id>/', DeleteQuestion.as_view(), name='delete_question'),
    path('retrieve_question/', RetrieveQuestion.as_view(), name='retrieve_all_questions'),
    path('event_question_create/<int:event_id>/', EventQuestionCreate.as_view(), name='event_question_create'),
    

]
