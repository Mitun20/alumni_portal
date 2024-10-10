from datetime import datetime
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import *
from account.models import Member
from django.db.models import Q

class CreateTicket(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the Member object associated with the authenticated user
        member = Member.objects.get(user=request.user)
        # Get the Alumni object associated with the Member
        alumni = Alumni.objects.get(member=member)

        category = TicketCategory.objects.get(id=request.data.get('category'))  # Assuming category ID is provided
        status = TicketStatus.objects.get(status='Submitted')  # Assuming status ID is provided
        
        ticket = Ticket(
            alumni=alumni,
            category=category,
            status=status,
            priority=request.data.get('priority'),
            due_date=request.data.get('due_date'),
            content=request.data.get('content'),
            assign_to=request.data.get('assign_to'),  # Assuming this is a user ID
        )
        
        ticket.save()
        return Response({"message": "Ticket created successfully"}, status=status.HTTP_201_CREATED)

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
                'category': ticket.category.name,  # Adjust based on your TicketCategory model
                'status': ticket.status.name,  # Adjust based on your TicketStatus model
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
                'assign_to': ticket.assign_to.username if ticket.assign_to else None,  # Assuming User has a username field
            })

        return Response(tickets_data, status=status.HTTP_200_OK)

class RetrieveTicket(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tickets = Ticket.objects.all()
        
        # Manually create a list of ticket data
        tickets_data = []
        for ticket in tickets:
            tickets_data.append({
                'id': ticket.id,
                'alumni': ticket.alumni.member.email,  # Adjust based on your Alumni model
                'category': ticket.category.name,  # Adjust based on your TicketCategory model
                'status': ticket.status.name,  # Adjust based on your TicketStatus model
                'priority': ticket.priority,
                'due_date': ticket.due_date,
                'last_status_on': ticket.last_status_on,
                'content': ticket.content,
                'assign_to': ticket.assign_to.username if ticket.assign_to else None,  # Assuming User has a username field
            })

        return Response(tickets_data, status=status.HTTP_200_OK)
    
# get all user has faculty group
class FacultyUsers(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get the 'Faculty' group
        faculty_group = Group.objects.get(name='Faculty')

        if faculty_group:
            # Retrieve users belonging to the 'Faculty' group
            users = User.objects.filter(groups=faculty_group)
            # Create a list of user data dictionaries
            user_data = [{'id': user.id, 'username': user.username, 'email': user.email} for user in users]
            return Response(user_data)
        else:
            return Response({'detail': 'Group not found.'}, status=404)
        
class TicketAssignTo(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,ticket_id):
        
        assigned_to_id = request.data.get('assigned_to')  # Get the assigned user ID from the request
        
        # Fetch the ticket and assigned user
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            assigned_to = User.objects.get(id=assigned_to_id)
            ticket.assign_to = assigned_to
        except (Ticket.DoesNotExist, User.DoesNotExist):
            return Response({"error": "Invalid ticket or user ID"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the TicketAssignment
        ticket_assignment = TicketAssignment(
            ticket=ticket,
            assigned_to=assigned_to,

        )
        ticket.status = TicketStatus.objects.get(status='Assigned')
        ticket_assignment.save()
        return Response({"message": "Ticket assigned successfully"}, status=status.HTTP_201_CREATED)


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
                'ticket_category': assignment.ticket.category,
                'ticket_content': assignment.ticket.content,  # Assuming Ticket has a content field
                'assigned_on': assignment.assigned_on,

            })

        return Response(assignments_data, status=status.HTTP_200_OK)

class ResponceTicketAssignment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, assignment_id):
        try:
            # Fetch the TicketAssignment object
            ticket_assignment = TicketAssignment.objects.get(id=assignment_id)
            responce = request.data['responce']
            # Check if the request user is the assigned user
            # if ticket_assignment.assigned_to != request.user:
            #     return Response({"error": "You do not have permission to update this assignment"}, status=status.HTTP_403_FORBIDDEN)

            ticket_assignment.response = responce
            ticket_assignment.respond_on = datetime.now()
            ticket_assignment.save()
            return Response({"message": "Ticket assignment updated successfully"}, status=status.HTTP_200_OK)
        
        except TicketAssignment.DoesNotExist:
            return Response({"error": "Ticket assignment not found"}, status=status.HTTP_404_NOT_FOUND)
        
class TicketStatusUpdate(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, ticket_id):
        # Get the ticket and status
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            status = TicketStatus.objects.get(id=request.data.get('status'))
        except (Ticket.DoesNotExist, TicketStatus.DoesNotExist):
            return Response({"error": "Invalid ticket or status ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the ticket status
        ticket.status = status
        ticket.last_status_on = datetime.now()
        ticket.save()
        
        return Response({"message": "Ticket status updated successfully"}, status=status.HTTP_200_OK)

class TicketReply(APIView):
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, ticket_id):
        # Get the ticket comment and reply text
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            reply_text = request.data.get('reply')
        except (Ticket.DoesNotExist, ValueError):
            return Response({"error": "Invalid ticket or reply text"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the TicketReply
        ticket_reply = TicketReply(
            ticket=ticket,
            message=reply_text,
            posted_by=request.user,  # Assuming User has a foreign key to Member
        )
        
        ticket_reply.save()
        return Response({"message": "Ticket reply created successfully"}, status=status.HTTP_201_CREATED)

class TicketClose(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def post(self, request, ticket_id):
        # Get the ticket
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"error": "Invalid ticket ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update the ticket status to closed
        ticket.status = TicketStatus.objects.get(status= 'Close')
        ticket.save()
        
        return Response({"message": "Ticket closed successfully"}, status=status.HTTP_200_OK)

class TicketFilterView(APIView):
    permission_classes = [IsAuthenticated]

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
            data.append({
                "id": ticket.id,
                "alumni": ticket.alumni.name,  # Adjust as necessary for the alumni's name
                "category": ticket.category.category,
                "status": ticket.status.status,
                "priority": ticket.priority,
                "due_date": ticket.due_date,
                "content": ticket.content,
                "assigned_to": ticket.assign_to.username if ticket.assign_to else None,
                "last_status_on": ticket.last_status_on,
            })

        return Response(data, status=status.HTTP_200_OK)
