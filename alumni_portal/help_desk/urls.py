from django.urls import path
from .views import *



urlpatterns = [
    path('retrieve_status/', TicketStatusList.as_view(), name='retrieve_status'),
    
    # Category
    path('create_ticket_category/', CreateTicketCategory.as_view(), name='create_ticket_category'),
    path('retrieve_ticket_category/', RetrieveTicketCategory.as_view(), name='retrieve_ticket_category'),
    path('update_ticket_category/<int:category_id>/', UpdateTicketCategory.as_view(), name='update_ticket_category'),
    
    # alumni handling Ticket
    path('create_ticket/', CreateTicket.as_view(), name='create_ticket'),
    path('my_ticket/', MyTicket.as_view(), name='my_ticket'),
    path('detail_my_ticket/<int:ticket_id>/', DetailMyTicket.as_view(), name='detail_my_ticket'),
        
    # Manager handling ticket
    path('retrieve_ticket/', RetrieveTicket.as_view(), name='retrieve_ticket'),
    path('retrieve_open_ticket/', RetrieveOpenTicket.as_view(), name='retrieve_open_ticket'),
    path('detail_ticket/<int:ticket_id>/', DetailTicket.as_view(), name='detail_ticket'),
    path('faculty_users/', FacultyUsers.as_view(), name='faculty_users'),
    path('assign_ticket/<int:ticket_id>/', TicketAssignTo.as_view(), name='assign_ticket'),
    path('assigned_user_ticket/<int:ticket_id>/', AssignedUsersForTicket.as_view(), name='assigned_user_ticket'),
    path('irresponse_ticket/', IrresponseTicket.as_view(), name='irresponse_ticket'),
    path('responced_ticket/', ResponcedTicket.as_view(), name='responced_ticket'),
    path('reply_ticket/<int:ticket_id>/',ReplyTicket.as_view(),name='reply_ticket'),
    path('tickets_replies/<int:ticket_id>/', TicketReplies.as_view(), name='ticket_replies'),
    
    # Facuylty handling ticket
    path('assignments/', MyTicketAssignment.as_view(), name='assignments'),
    path('respond_ticket/<int:assignment_id>/', ResponceTicketAssignment.as_view(), name='respond_ticket'),
    path('update_status/<int:ticket_id>/', TicketStatusUpdate.as_view(), name='update_status'),
    
    # path('close_ticket/<int:ticket_id>/',TicketClose.as_view(),name='close_ticket'),

    # Filter Ticket    
    path('filter_ticket/', TicketFilterView.as_view(), name='filter_ticket'),
    path('open_filter_ticket/', TicketFilterOpenView.as_view(), name='open_filter_ticket'),
    path('replied_filter_ticket/', TicketFilterRepliedView.as_view(), name='replied_filter_ticket'),
    

]
