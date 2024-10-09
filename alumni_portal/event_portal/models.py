# from django.db import models
# from django.contrib.auth.models import User

# # Event Category Model
# class EventCategory(models.Model):
#     title = models.CharField(max_length=225)

#     def __str__(self):
#         return self.title

# # Event Model
# class Event(models.Model):
#     title = models.CharField(max_length=255)
#     category = models.ForeignKey(EventCategory, on_delete=models.CASCADE)
#     start_date = models.DateField()
#     start_time = models.TimeField()
#     venue = models.CharField(max_length=225)
#     address = models.TextField(blank=True, null=True)
#     link = models.URLField(max_length=255, blank=True, null=True)
#     is_public = models.BooleanField(default=True)
#     need_registration = models.BooleanField(default=True)
#     registration_close_date = models.DateField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     event_wallpaper = models.ImageField(upload_to='events/wallpapers/', blank=True, null=True)
#     instructions = models.TextField(blank=True, null=True)
#     posted_on = models.DateField(auto_now_add=True)
#     posted_by = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.title

# # Event Question Model
# class EventQuestion(models.Model):
#     question = models.CharField(max_length=225)
#     options = models.CharField(max_length=225, blank=True, null=True)
#     help_text = models.CharField(max_length=225, blank=True, null=True)
#     is_faq = models.BooleanField(default=False)

#     def __str__(self):
#         return self.question

# # Event Registration Model
# class EventRegistration(models.Model):
#     event = models.ForeignKey(Event, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     applied_on = models.DateField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} registered for {self.event.title}"

# # Registration Response Model
# class RegistrationResponse(models.Model):
#     registered_event = models.ForeignKey(EventRegistration, on_delete=models.CASCADE)
#     question = models.ForeignKey(EventQuestion, on_delete=models.CASCADE)
#     response = models.CharField(max_length=255)

#     def __str__(self):
#         return f"Response to {self.question.question} by {self.registered_event.user.username}"


