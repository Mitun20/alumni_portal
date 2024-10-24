import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import *
from account.permissions import *
from .serializers import *

# manage category
class CreateEventCategory(APIView):
    # permission_classes = [IsAuthenticated, IsAlumniManagerOrAdministrator]

    def post(self, request):
        event_category = EventCategory(
            title=request.data['category'],
        )
        event_category.save()

        return Response({"message": "Event category created successfully"}, status=status.HTTP_201_CREATED)

class RetrieveEventCategory(APIView):
    def get(self, request):
        event_categories = EventCategory.objects.all()
        data = [
            {
                "category_id": event_category.id,
                "title": event_category.title,
            }
            for event_category in event_categories
        ]
        return Response(data, status=status.HTTP_200_OK)

class UpdateEventCategory(APIView):
    def Post(self, request, category_id):
        try:
            event_category = EventCategory.objects.get(id=category_id)
            event_category.title = request.data.get('category', event_category.title)
            event_category.save()
            return Response({"message": "Event category updated successfully"}, status=status.HTTP_200_OK)
        except EventCategory.DoesNotExist:
            return Response({"error": "Event category not found"}, status=status.HTTP_404_NOT_FOUND)
#---------------------------------------------------- manage Event
class CreateEvent(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Create a copy of the request.data and add posted_by to it
        event_data = request.data.copy()
        event_data['posted_by'] = request.user.id  # Add the current user's ID
        
        serializer = EventSerializer(data=event_data)
        
        if serializer.is_valid():
            event = serializer.save()  # Save the event and get the instance
            
            return Response({
                "message": "Event created successfully",
                "event_id": event.id  # Return the created event ID
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveEvent(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        events = Event.objects.all()  # Retrieve all events
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateEvent(APIView):
    permission_classes = [IsAuthenticated]  # Add any specific permissions if needed

    def get(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            serializer = EventSerializer(event, context={'request': request})  # Pass request context
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND)


    def post(self, request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            serializer = EventSerializer(event, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Event updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            return Response({"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

class DeactivateEvent(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, event_id):
        try:
            event = Event.objects.get(id=event_id)
            event.is_active = request.data.get('is_active')
            event.save()
            if event.is_active:
                return Response({"message": "Event activated successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Event deactivated successfully"}, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({"message": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

# active Event

class ActiveEvent(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        events = Event.objects.filter(is_active=True)
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# Event by category
class EventByCategory(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, category_id):
        events = Event.objects.filter(category_id=category_id)
        serializer = EventSerializer(events, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

#------------------------------------------------------- manage question

class CreateQuestion(APIView):
    def post(self, request):
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Question Created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# create custom question
class CreateEventQuestion(APIView):
    def post(self, request,event_id):
        
        # Validate if the event exists
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create the question
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.save()

            # Create the EventQuestion entry
            EventQuestion.objects.create(event=event, question=question)

            return Response({"message": "Question created successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RetrieveQuestion(APIView):
    def get(self, request, question_id=None):
        if question_id:
            try:
                question = Question.objects.get(id=question_id)
                serializer = QuestionSerializer(question)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Question.DoesNotExist:
                return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateQuestion(APIView):
    def get(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
            
    def post(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            serializer = QuestionSerializer(question, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Question updated successfully"}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

class DeleteQuestion(APIView):
    def delete(self, request, question_id):
        try:
            question = Question.objects.get(id=question_id)
            question.delete()
            return Response({"message": "Question deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)
        
# map event with question

class EventQuestionCreate(APIView):
    def post(self, request, event_id):
        # Create multiple EventQuestions
        questions_data = request.data.get('questions', [])

        created_questions = []
        for question_id in questions_data:
            try:
                event_question = EventQuestion.objects.create(event_id=event_id, question_id=question_id)
                created_questions.append({"id": event_question.id, "question_id": question_id})
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "EventQuestions created successfully", "questions": created_questions}, status=status.HTTP_201_CREATED)

    def get(self, request, event_id):
        # Retrieve all EventQuestions for the specified event
        event_questions = EventQuestion.objects.filter(event_id=event_id).all()
        data=[]
        for event_question in event_questions:
            print(event_question.question.id)
            data.append({
                "id": event_question.id,
                "question_id": event_question.question.id,
                "question": event_question.question.question,
                "options": event_question.question.options,
                "help_text": event_question.question.help_text,
                "is_faq": event_question.question.is_faq,
            })
        return Response(data, status=status.HTTP_200_OK)

class EventQuestionDelete(APIView):
    
    def delete(self, request, event_question_id):
        # Delete a specific EventQuestion
        try:
            event_question = EventQuestion.objects.get(id=event_question_id)
            event_question.delete()
            return Response({"message": "EventQuestion deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except EventQuestion.DoesNotExist:
            return Response({"error": "EventQuestion not found"}, status=status.HTTP_404_NOT_FOUND)