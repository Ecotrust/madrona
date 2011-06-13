from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from models import UserProfile
from lingcod.features.forms import FeatureForm as UserForm
from forms import UserProfileForm
from django.conf import settings
from django.core.urlresolvers import reverse
from lingcod.openid.models import UserAssociation

@login_required
def profile_form(request,username,use_openid=False):
    if request.user.username != username:
        return HttpResponse( "You cannot access another user's profile.", status=401)
    else:
        user = User.objects.get(username=username)
        try:
            user_profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=user)

    user_assoc = UserAssociation.objects.filter(user__id=user.id)
    
    if request.method == 'GET':
        uform = UserForm(instance=user)
        pform = UserProfileForm(instance=user_profile)
        return render_to_response('user_profile/user_profile_form.html', 
                {'profile': user_profile, 'assoc': user_assoc, 'uform': uform, 'pform': pform, 
                    'group_request_email': settings.GROUP_REQUEST_EMAIL, 'use_openid': use_openid, 'MEDIA_URL':settings.MEDIA_URL}) 

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
