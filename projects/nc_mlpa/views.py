from django.shortcuts import redirect
from mlpa.models import *
from lingcod.mpa.views import *

def manipulatorList(request):
    return redirect('/manipulators/list/mlpa/mlpampa/')