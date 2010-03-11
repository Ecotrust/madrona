from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import UserProfile
from forms import UserForm, UserProfileForm
from django.conf import settings
from django.core.urlresolvers import reverse

@login_required
def profile_form(request,username):
    if request.user.username != username:
        return HttpResponse( "You cannot access another user's profile.", status=401)
    else:
        user = User.objects.get(username=username)
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user)

    if request.method == 'GET':
        uform = UserForm(instance=user)
        pform = UserProfileForm(instance=user_profile)
        return render_to_response('user_profile/user_profile_form.html', 
                {'profile': user_profile, 'uform': uform, 'pform': pform, 
                'group_request_email': settings.GROUP_REQUEST_EMAIL, 'MEDIA_URL':settings.MEDIA_URL}) 

    elif request.method == 'POST':
        uform = UserForm(data=request.POST, instance=user)
        pform = UserProfileForm(data=request.POST, instance=user_profile)
        if uform.is_valid():
            user.save()
        if pform.is_valid():
            user_profile.save()

        #return HttpResponseRedirect(reverse('user_profile-form', args=[username]))
        return HttpResponseRedirect(reverse('map'))
    else:
        return HttpResponse( "Received unexpected " + request.method + " request.", status=400 )
