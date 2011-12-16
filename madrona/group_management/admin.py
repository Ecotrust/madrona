from django.contrib import admin
from madrona.group_management.models import GroupRequest

class GroupRequestAdmin(admin.ModelAdmin):
    pass

admin.site.register(GroupRequest, GroupRequestAdmin)
