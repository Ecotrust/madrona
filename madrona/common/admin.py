# utils/admin_auth.py
# -*- coding: utf-8 -*-
# derived from http://www.djangosnippets.org/snippets/1650/
from django.utils.safestring import mark_safe
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib import admin
from django.urls import reverse


def roles(self):
    #short_name = unicode # function to get group name
    p = sorted([u"<a title='%s'>%s</a>" % (x, x) for x in self.groups.all()])
    if self.user_permissions.count():
        p += ['+']
    value = ' | '.join(p)
    return mark_safe("%s" % value)
roles.allow_tags = True
roles.short_description = u'Groups'

def last(self):
    fmt = "%b %d, %H:%M"
    #fmt = "%Y %b %d, %H:%M:%S"
    value = self.last_login.strftime(fmt)
    return mark_safe("<nobr>%s</nobr>" % value)
last.allow_tags = True
last.admin_order_field = 'last_login'

def adm(self):
    return self.is_superuser
adm.boolean = True
adm.admin_order_field = 'is_superuser'

def staff(self):
    return self.is_staff
staff.boolean = True
staff.admin_order_field = 'is_staff'

def persons(self):
    return ', '.join(['<a href="%s">%s</a>' % (reverse('admin:auth_user_change', args=(x.id,)), x.username) for x in self.user_set.all().order_by('username')])
persons.allow_tags = True

class GroupMembersInline(admin.TabularInline):
    model = User.groups.through
    verbose_name = 'Group member'
    verbose_name_plural = 'Group members'
    extra = 3

def allow_share_to_staff(modeladmin, request, queryset):
    from django.conf import settings
    sg = settings.SHARING_TO_STAFF_GROUPS
    if hasattr(sg,'__iter__') and len(sg) > 0:
        for g in sg:
            group_obj = Group.objects.get(name=g)
            for user in queryset:
                user.groups.add(group_obj)
                user.save()
allow_share_to_staff.short_description = "Allow selected users to share to staff for review"

def remove_users_from_all_groups(modeladmin, request, queryset):
    for user in queryset:
        user.groups.clear()
        user.save()
remove_users_from_all_groups.short_description = "Remove all group associations from selected users"

class UserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', staff, adm, roles, last]
    list_filter = ['groups', 'is_staff', 'is_superuser', 'is_active']
    actions = [allow_share_to_staff, remove_users_from_all_groups]

class GroupAdmin(GroupAdmin):
    list_display = ['name', persons]
    list_display_links = ['name']
    inlines = (GroupMembersInline,)

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)
