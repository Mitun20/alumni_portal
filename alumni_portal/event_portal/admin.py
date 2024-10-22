from django.contrib import admin
from .models import *

admin.site.register(Event)
admin.site.register(EventCategory)
admin.site.register(EventComment)
admin.site.register(EventLike)
admin.site.register(EventQuestion)
admin.site.register(EventRegistration)
admin.site.register(RegistrationResponse)
admin.site.register(Question)
