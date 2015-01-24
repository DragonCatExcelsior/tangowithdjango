from django.shortcuts import render
from django.http import HttpResponse

def index(request):

    #Construct a dictionary to pass to the template engine as its conext.
    #Note the key boldmessage is the same as {{ boldmessage }} in the template!
    context_dict = {'boldmessage': "I am bold font from the context"}

    #Return a rendered response to the client.
    #We make use of the shortcut function to make our lives easier.
    #Note that the first parameter is the template we wish to use.

    return render(request, 'rango/index.html', context_dict)

    #Old index() function.
    #return HttpResponse("Rango says: Hello world! <p><a href='/rango/about'>About</a></p>")

def about(request):
    context_dict = { 'boldmessage': "This tutorial has been put together by Jake Degiovanni, 2066890"}

    return render(request, 'rango/about.html', context_dict)

    #return HttpResponse("Rango says here is the about page. "
    #                    "<p>This tutorial has been put together by Jake Degiovanni, 2066890</p>"
    #                    "<p><a href='/rango/'>Index</a></p>")
