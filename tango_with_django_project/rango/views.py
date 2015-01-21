from django.http import HttpResponse

def index(request):
    return HttpResponse("Rango says: Hello world! <p><a href='/rango/about'>About</a></p>")

def about(request):
    return HttpResponse("Rango says here is the about page. "
                        "<p>This tutorial has been put together by Jake Degiovanni, 2066890</p>"
                        "<p><a href='/rango/'>Index</a></p>")
