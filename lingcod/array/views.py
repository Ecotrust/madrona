from django.http import HttpResponse
from django.shortcuts import render_to_response
from lingcod.common import utils 

Mpa = utils.get_mpa_class()
MpaArray = utils.get_array_class()

def add_mpa(request, pk):
    '''
        Add and MPA to a given array
    '''
    if request.method == 'POST':
        try:
            mpa_id = request.REQUEST['mpa_id']
        except:
            return HttpResponse( "Must supply an 'mpa_id' parameter.", status=500 )

        # Make sure user owns both the array and MPA
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse('You must be logged in', status=401)

        # Get MPA object 
        # print Mpa.objects.all()
        try:
            the_mpa = Mpa.objects.get(user=user,id=mpa_id)
        except:
            return HttpResponse( user.username + " does not own an MPA with ID " + mpa_id, status=404 )

        # If MPA already has an array, return an error
        if the_mpa.array:
            return HttpResponse( "MPA " + mpa_id + " is already associated with another array.", status=500 )

        # Get array object
        try:
            the_array = MpaArray.objects.get(user=user,id=pk)
        except:
            return HttpResponse( user.username + " does not own an Array with ID " + pk, status=404 )

        # Add the MPA to the array
        the_mpa.add_to_array(the_array)
        return HttpResponse("Added mpa %s to array %s" % (mpa_id, pk))
    else:
        return HttpResponse( "Array-MPA service received unexpected " + request.method + " request.", status=400 )

def remove_mpa(request, pk):
    '''
        Remove an MPA from its array
    '''
    if request.method == 'POST':
        try:
            mpa_id = request.REQUEST['mpa_id']
        except:
            return HttpResponse( "Must supply an 'mpa_id' parameter.", status=500 )

        # Make sure user owns MPA
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse('You must be logged in', status=401)

        # Get MPA object 
        try:
            the_mpa = Mpa.objects.get(user=user,id=mpa_id)
        except:
            return HttpResponse( user.username + " does not own an MPA with ID " + mpa_id, status=404 )

        # If MPA is not in any array, return an error since there is nothing to remove
        if not the_mpa.array:
            return HttpResponse( "MPA " + mpa_id + " is not associated with another array (nothing to remove).", status=500 )

        # Get array object and make sure it is owned by user 
        try:
            the_array = MpaArray.objects.get(user=user,id=pk)
        except:
            return HttpResponse( user.username + " does not own an Array with ID " + pk, status=404 )
        # and make sure we're trying to remove it from the right array
        if the_mpa.array != the_array:
            return HttpResponse( "Trying to remove mpa %s from array %s but it currently belongs to another array " % 
                                  (mpa_id, pk), status=500 )

        # Remove the MPA from the array
        the_mpa.remove_from_array()
        return HttpResponse("Removed MPA %s from array %s" % (mpa_id, pk))
    else:
        return HttpResponse( "Array-MPA service received unexpected " + request.method + " request.", status=400 )


def copy(request, pk):
    """
    Creates a copy of the given array 
    On success, Return status 201 with Location set to new MPA
    Permissions: Need to either own or have shared with you to make copy
    """
    if request.method == 'POST' or request.method == 'GET': # MP TODO POST only
        # Authenticate
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse(txt + 'You must be logged in', status=401)

        try:
            # Frst see if user owns it
            the_array = MpaArray.objects.get(id=int(pk), user=user)
        except MpaArray.DoesNotExist:
            try: 
                # ... then see if its shared with the user
                the_array = MpaArray.objects.shared_with_user(user).get(id=int(pk))
            except MpaArray.DoesNotExist:
                txt = "You dont own it and nobdy shared it with you so you can't make a copy."
                return HttpResponse(txt, status=401)
        
        # Go ahead and make a copy
        new_array = the_array.copy(user)

        Location = new_array.get_absolute_url()
        res = HttpResponse("A copy of Array %s was made; see %s" % (pk, Location), status=201)
        res['Location'] = Location
        return res
    else:
        return HttpResponse( "Array copy service received unexpected " + request.method + " request.", status=400 )
