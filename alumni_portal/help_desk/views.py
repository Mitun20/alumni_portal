from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import *
from account.models import Member
from django.db.models import Q
from django.shortcuts import get_object_or_404

#  retrieve status
class TicketStatusList(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        statuses = TicketStatus.objects.all()
        status_list = [{"id": status.id, "status": status.status} for status in statuses]
        return Response(status_list, status=status.HTTP_200_OK)
    
# manage category
class CreateTicketCategory(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        category = TicketCategory(category=request.data['category'])
        category.save()
        return Response({"message": "Ticket category created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveTicketCategory(APIView):
    def get(self, request):
        categories = TicketCategory.objects.all()
        data = [
            {
                "id": category.id,
                "category": category.category
            }
            for category in categories
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateTicketCategory(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, category_id):
        try:
            category = TicketCategory.objects.get(id=category_id)
            data = {
                "category": category.category
            }
            return Response(data, status=status.HTTP_200_OK)
        except TicketCategory.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, category_id):
        try:
            category = TicketCategory.objects.get(id=category_id)
        except TicketCategory.DoesNotExist:
            return Response({"message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        category.category = request.data["category"]
        category.save()

        return Response({"message": "Category updated successfully"}, status=status.HTTP_200_OK)



# #  retrieve category
# class TicketCategoryList(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request):
#         categories = TicketCategory.objects.all()
#         category_list = [{"id": category.id, "category": category.category} for category in categories]
#         return Response(category_list, status=status.HTTP_200_OK)

#  create tickets
class CreateTicket(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the Member object associated with the authenticated user
        member = Member.objects.get(user=request.user)
        
        # Get the Alumni object associated with the Member
        alumni = Alumni.objects.get(member=member)

        # Prepare the response data
        response_data = {
            "full_name": alumni.member.user.get_full_name(),  # Assuming User has a get_full_name method
            "email": alumni.member.email,
            "contact": alumni.member.mobile_no,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def post(self, request):
        # Get the Member object associated with the authenticated user
        member = Member.objects.get(user=request.user)
        
        # Get the Alumni object associated with the Member
        alumni = Alumni.objects.get(member=member)

        category = TicketCategory.objects.get(id=request.data.get('category'))
        ticket_status = get_object_or_404(TicketStatus, status='Open')

        ticket = Ticket(
            alumni=alumni,
            category=category,
            status=ticket_status,
            priority=request.data.get('priority'),
            due_date=request.data.get('due_date'),
            content=request.data.get('content'),
        )
        
        ticket.save()
        return Response({"message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)

# my tickets
class MyTicket(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the Member object associated with the authenticated user
        member = Member.objects.get(user=request.user)
        # Get the Alumni object associated with the Member
        alumni = Alumni.objects.get(member=member)

        # Get tickets associated with the Alumni
        tickets = Ticket.objects.filter(alumni=alumni)
        
        # Manually create a list of ticket data
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'category': ticket.category.category,  # Adjust based on your TicketCategory model
                'status': ticket.status.status,  # Adjust based on your TicketStatus model
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
            })

        return Response(tickets_data, status=status.HTTP_200_OK)

# Retrieve all tickets
class RetrieveTicket(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.all()
        
        tickets_data = []
        for ticket in tickets:
            full_name = f"{ticket.alumni.member.user.first_name} {ticket.alumni.member.user.last_name}"
            tickets_data.append({
                'id': ticket.id,
                'name': full_name,
                'batch': ticket.alumni.member.batch.title,
                'end_year': ticket.alumni.member.batch.end_year,
                'alumni': ticket.alumni.member.email,
                'contact': ticket.alumni.member.email,
                'category': ticket.category.category, 
                'status': ticket.status.status, 
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
            })

        return Response(tickets_data, status=status.HTTP_200_OK)
    
# get open ticket
class RetrieveOpenTicket(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.filter(status__status="Open")
        
        tickets_data = []
        for ticket in tickets:
            full_name = f"{ticket.alumni.member.user.first_name} {ticket.alumni.member.user.last_name}"
            tickets_data.append({
                'id': ticket.id,
                'name': full_name,
                'batch': ticket.alumni.member.batch.title,
                'end_year': ticket.alumni.member.batch.end_year,
                'alumni': ticket.alumni.member.email,
                'contact': ticket.alumni.member.email,
                'category': ticket.category.category, 
                'status': ticket.status.status, 
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
            })

        return Response(tickets_data, status=status.HTTP_200_OK)


# get all faculty 
class FacultyUsers(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        faculty_group = Group.objects.get(name='Faculty')

        if faculty_group:
            users = User.objects.filter(groups=faculty_group)
            user_data = [{'id': user.id, 'username': user.username} for user in users]
            return Response(user_data)
        else:
            return Response({'detail': 'Group not found.'}, status=404)
        
# assign tickets to faculty
class TicketAssignTo(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        assigned_to_id = request.data.get('faculty_id')  # Get the assigned user ID from the request
        message = request.data.get('message')
        
        # Fetch the ticket and assigned user
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket_status = get_object_or_404(TicketStatus, status='Assigned')
            ticket.status = ticket_status
            ticket.last_status_on = datetime.now()
            ticket.save()
            assigned_to = User.objects.get(id=assigned_to_id)
            
        except (Ticket.DoesNotExist, User.DoesNotExist):
            return Response({"error": "Invalid ticket or user ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Check for existing TicketAssignment for the same ticket
        # existing_assignment = TicketAssignment.objects.filter(ticket=ticket).first()
        # if existing_assignment:
        #     return Response({"error": "This ticket is already assigned."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the TicketAssignment
        ticket_assignment = TicketAssignment(
            ticket=ticket,
            assigned_to=assigned_to,
            message=message
        )
        ticket_assignment.save()
        return Response({"message": "Ticket assigned successfully"}, status=status.HTTP_201_CREATED)

# My Assignments
class MyTicketAssignment(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the assigned ticket assignments for the authenticated user
        assigned_tickets = TicketAssignment.objects.filter(assigned_to=request.user,ticket__status__status="Assigned")
        
        # Create a list of assignments data
        assignments_data = []
        for assignment in assigned_tickets:
            assignments_data.append({
                'id': assignment.id,
                'ticket_id': assignment.ticket.id,
                'ticket_category': assignment.ticket.category.category,
                'status': assignment.ticket.status.status,
                # 'ticket_content': assignment.ticket.content, 
                'assigned_on': assignment.assigned_on,
                'message':assignment.message,
                'priority': assignment.ticket.priority,
                # 'last_status_on': assignment.ticket.last_status_on,
            })

        return Response(assignments_data, status=status.HTTP_200_OK)

# Respond Ticket
class ResponceTicketAssignment(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, assignment_id):
        try:
            # Fetch the TicketAssignment object
            ticket_assignment = TicketAssignment.objects.get(id=assignment_id)
            responce = request.data['responce']
            
            # Check if the response is already set
            if ticket_assignment.response:
                return Response({"error": "Response has already been submitted for this assignment."}, status=status.HTTP_400_BAD_REQUEST)
            # Check if the request user is the assigned user
            # if ticket_assignment.assigned_to != request.user:
            #     return Response({"error": "You do not have permission to update this assignment"}, status=status.HTTP_403_FORBIDDEN)

            ticket_assignment.response = responce
            ticket_assignment.respond_on = datetime.now()
            ticket_assignment.ticket.status = get_object_or_404(TicketStatus, status='Replied')
            ticket_assignment.save()
            return Response({"message": "Ticket Responce updated successfully"}, status=status.HTTP_200_OK)
        
        except TicketAssignment.DoesNotExist:
            return Response({"error": "Ticket assignment not found"}, status=status.HTTP_404_NOT_FOUND)

# All responced tickets
class ResponcedTicket(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the assigned ticket assignments for the authenticated user
        assigned_tickets = TicketAssignment.objects.filter(ticket__status__status="Replied")
        
        # Create a list of assignments data
        assignments_data = []
        for assignment in assigned_tickets:
            assignments_data.append({
                'id': assignment.id,
                'ticket_id': assignment.ticket.id,
                'ticket_category': assignment.ticket.category.category,
                'status': assignment.ticket.status.status,
                # 'ticket_content': assignment.ticket.content, 
                'assigned_on': assignment.assigned_on,
                'message':assignment.message,
                'priority': assignment.ticket.priority,
                # 'last_status_on': assignment.ticket.last_status_on,
            })

        return Response(assignments_data, status=status.HTTP_200_OK)


# responce for specific ticket assignment 
class TicketAssignmentResponse(APIView):
    def get(self, request, ticket_assignment_id):
        try:
            ticket_assignment = TicketAssignment.objects.get(ticket_id=ticket_assignment_id)
            
            # Prepare the response data
            response_data = {
                "response": ticket_assignment.response,
                "respond_on": ticket_assignment.respond_on
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except TicketAssignment.DoesNotExist:
            return Response({"error": "No assignment found for this ticket"}, status=status.HTTP_404_NOT_FOUND)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
        
# Ticket Status Update
class TicketStatusUpdate(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, ticket_id):
        # Get the ticket and status
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            full_name = f"{ticket.alumni.member.user.first_name} {ticket.alumni.member.user.last_name}"
            ticket_data = {
                'id': ticket.id,
                'name': full_name,
                'batch': ticket.alumni.member.batch.title,
                'end_year': ticket.alumni.member.batch.end_year,
                'alumni': ticket.alumni.member.email,
                'contact': ticket.alumni.member.email,
                'category': ticket.category.category, 
                'status': ticket.status.status, 
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
            }
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(ticket_data, status=status.HTTP_200_OK)
    def post(self, request, ticket_id):
        # Get the ticket and update its status, priority, and due date
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            ticket_status_id = request.data.get('status')
            ticket_priority = request.data.get('priority')
            ticket_due_date = request.data.get('due_date')

            # Track if the status was updated
            status_changed = False

            # Update the status if provided
            if ticket_status_id:
                ticket_status = TicketStatus.objects.get(id=ticket_status_id)
                if ticket.status != ticket_status:
                    ticket.status = ticket_status
                    status_changed = True

            # Update the priority if provided
            if ticket_priority and ticket_priority in dict(Ticket.PRIORITY_CHOICES):
                ticket.priority = ticket_priority

            # Update the due date if provided
            if ticket_due_date:
                ticket.due_date = ticket_due_date  # Ensure this is a valid date format

            # Update the last status date only if status changed
            if status_changed:
                ticket.last_status_on = datetime.now()

            ticket.save()
        
        except (Ticket.DoesNotExist, TicketStatus.DoesNotExist):
            return Response({"error": "Invalid ticket or status ID"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Ticket updated successfully"}, status=status.HTTP_200_OK)

# reply ticket
class ReplyTicket(APIView):
    # permission_classes = [IsAuthenticated]
    
    def post(self, request, ticket_id):
        # Get the ticket comment and reply text
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            reply_text = request.data.get('message')
        except (Ticket.DoesNotExist, ValueError):
            
            return Response({"error": "Invalid ticket or reply text"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the TicketReply
        ticket_reply = TicketReply(
            ticket=ticket,
            message=reply_text,
            posted_by=request.user  # Assuming User has a foreign key to Member
        )
        ticket_reply.save()
        return Response({"message": "Ticket replied successfully"}, status=status.HTTP_201_CREATED)
    
# replies for specific ticket
class TicketReplies(APIView):
    def get(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            replies = TicketReply.objects.filter(ticket=ticket)

            # Build a list of replies without using serializers
            reply_list = [
                {
                    "id": reply.id,
                    "message": reply.message,
                    "posted_on": reply.posted_on,
                    "posted_by": reply.posted_by.username  # Adjust this based on your User model
                }
                for reply in replies
            ]
            return Response(reply_list, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

# close ticket
class TicketClose(APIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, ticket_id):
        # Get the ticket
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"error": "Invalid ticket ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the ticket status to closed
        ticket.status = TicketStatus.objects.get(status= 'Closed')
        ticket.save()
        
        return Response({"message": "Ticket closed successfully"}, status=status.HTTP_200_OK)

# filter ticket
class TicketFilterView(APIView):
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Extract data from the JSON body
        status_id = request.data.get('status', None)  # Assuming you're passing the status ID
        category_id = request.data.get('category', None)  # Assuming you're passing the category ID
        priority = request.data.get('priority', None)
        due_date = request.data.get('due_date', None)  # Format as needed

        # Create a dictionary for the filter arguments
        filters = Q()
        if status_id:
            filters &= Q(status_id=status_id)
        if category_id:
            filters &= Q(category_id=category_id)
        if priority:
            filters &= Q(priority=priority)
        if due_date:
            filters &= Q(due_date=due_date)

        # Apply the filters in a single query
        queryset = Ticket.objects.filter(filters)

        # Prepare the response data
        data = []
        for ticket in queryset:
            full_name = f"{ticket.alumni.member.user.first_name} {ticket.alumni.member.user.last_name}"
            data.append({
                'id': ticket.id,
                'name': full_name,
                'batch': ticket.alumni.member.batch.title,
                'end_year': ticket.alumni.member.batch.end_year,
                'alumni': ticket.alumni.member.email,
                'contact': ticket.alumni.member.mobile_no,
                'category': ticket.category.category, 
                'status': ticket.status.status, 
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
            })

        return Response(data, status=status.HTTP_200_OK)