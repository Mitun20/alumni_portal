from django.contrib import admin
from .models import *

# Register each model using admin.site.register()

admin.site.register(JobPost)
admin.site.register(Application)
admin.site.register(JobComment)
admin.site.register(BusinessDirectory)
