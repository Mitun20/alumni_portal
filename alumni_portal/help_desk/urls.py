from django.urls import path
from .views import *



urlpatterns = [
    path('create_ticket/', CreateTicket.as_view(), name='create_ticket'),
    path('my_ticket/', MyTicket.as_view(), name='my_ticket'),
    
    path('retrieve_ticket/', RetrieveTicket.as_view(), name='retrieve_ticket'),

    # get users, groups and assign 
    path('faculty_users/', FacultyUsers.as_view(), name='faculty_users'),
    path('assign_ticket/', TicketAssignTo.as_view(), name='assign_ticket'),
    path('assignments/', MyTicketAssignment.as_view(), name='assignments'),
    path('respond_ticket/<int:user_id>/', ResponceTicketAssignment.as_view(), name='respond_ticket'),

    # alumni registration process
    path('register_user/', TicketStatusUpdate.as_view(), name='register_user'),
    path('creating_user/',TicketReply.as_view(),name='creating_user'),
    path('member_data/<int:member_id>/',TicketClose.as_view(),name='member_data'),

    # single or multiple created by manager
    path('single_import_users/', TicketFilterView.as_view(), name='single_import_users'),

    
]
