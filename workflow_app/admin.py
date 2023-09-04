from django.contrib import admin
from .models import *

admin.site.register(Staff)
admin.site.register(Manager)
admin.site.register(Task)
admin.site.register(AssignedTask)
admin.site.register(SelectedTask)