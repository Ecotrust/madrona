from django.http import HttpResponse

def main(request):
    return HttpResponse("News...")

def about(request):
    return HttpResponse("About...")
