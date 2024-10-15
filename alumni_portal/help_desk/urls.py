from django.urls import path
from .views import *



urlpatterns = [
    path('retrieve_status/', TicketStatusList.as_view(), name='retrieve_status'),
    path('retrieve_category/', TicketCategoryList.as_view(), name='retrieve_category'),
    path('create_ticket/', CreateTicket.as_view(), name='create_ticket'),
    path('my_ticket/', MyTicket.as_view(), name='my_ticket'),
    
    path('retrieve_ticket/', RetrieveTicket.as_view(), name='retrieve_ticket'),
    path('faculty_users/', FacultyUsers.as_view(), name='faculty_users'),
    path('assign_ticket/<int:ticket_id>/', TicketAssignTo.as_view(), name='assign_ticket'),
    path('assignments/', MyTicketAssignment.as_view(), name='assignments'),
    path('respond_ticket/<int:user_id>/', ResponceTicketAssignment.as_view(), name='respond_ticket'),

    path('update_status/', TicketStatusUpdate.as_view(), name='update_status'),
    path('reply_ticket/',TicketReply.as_view(),name='reply_ticket'),
    path('close_ticket/<int:member_id>/',TicketClose.as_view(),name='close_ticket'),

    path('filter_ticket/', TicketFilterView.as_view(), name='filter_ticket'),

    
]
