from django.contrib import admin
from .models import *

# Register each model using admin.site.register()

admin.site.register(TicketCategory)
admin.site.register(Ticket)
admin.site.register(TicketAssignment)
admin.site.register(TicketReply)
admin.site.register(TicketStatus)
