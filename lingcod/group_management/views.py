from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.conf import settings
from lingcod.group_management.models import GroupRequest
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

@login_required
def group_request(request):
    current_groups = request.user.groups.all()

    if request.method == 'GET':
        groups = Group.objects.all()
        if len(groups) == 0:
            return HttpResponse( "There are no potential groups at this time.", status=404)
        return render_to_response('group_management/group_request_form.html', 
                {'user':request.user, 'groups': groups, 'current_groups': current_groups, 'MEDIA_URL':settings.MEDIA_URL}) 
    elif request.method == 'POST':
        group_ids = [int(x) for x in request.POST.getlist('sharing_groups')]
        # Log the request instance (models.group_request) and send email to settings.GROUP_REQUEST_EMAIL & redirect to request/sent/
        groups = Group.objects.filter(pk__in=group_ids).exclude(pk__in=[x.pk for x in current_groups])
        for group in groups:
            gr = GroupRequest(user=request.user, group=group) 
            gr.save()
        if settings.GROUP_REQUEST_EMAIL:
            t = get_template('group_management/email_subject.txt')
            subject = t.render(Context({'user': request.user, 'groups': groups})).strip()

            t = get_template('group_management/email_body.txt')
            body = t.render(Context({'user': request.user, 'groups': groups}))

            send_mail(subject, body, settings.GROUP_REQUEST_EMAIL, [settings.GROUP_REQUEST_EMAIL], fail_silently=False)

        return HttpResponseRedirect(reverse('group_management-request-sent'))
    else:
        return HttpResponse( "Received unexpected " + request.method + " request.", status=400 )

