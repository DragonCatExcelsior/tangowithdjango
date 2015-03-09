from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import PageForm
from rango.forms import UserForm, UserProfileForm
from rango.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from rango.bing_search import run_query
from django.shortcuts import redirect

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method == 'GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']
            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass

    return redirect(url)

def register_profile(request):
    registered = False

    # A HTTP POST?
    if request.method == 'POST':
        profileForm = UserProfileForm(data = request.POST)

        if profileForm.is_valid():
            userProfile = profileForm.save(commit = False)
            userProfile.user = request.user

            if 'picture' in request.FILES:
                userProfile.picture = request.FILES['picture']

            userProfile.save()
            registered = True

        else:
            print profileForm.errors

    else:
        profileForm = UserProfileForm()

    return render(request, "rango/profile_registration.html/", {'profile_form': profileForm,'registered': registered})

def profile(request):
    user = request.user
    context_dict = {}
    context_dict['user'] = user

    try:
        own_profile = UserProfile.objects.get(user=user)
        context_dict['own_profile'] = own_profile

    except:
        own_profile = None
        context_dict['own_profile'] = own_profile

    return render(request, 'rango/profile.html', context_dict)

@login_required
def edit_profile(request):
    registered = False

    if request.method == "POST":

        try:
            profile = UserProfile.objects.get(user=request.user)
            profileForm = UserProfileForm(request.POST, instance = profile)
        except:
            profileForm = UserProfileForm(request.POST)

        if profileForm.is_valid():

            if request.user.is_authenticated():
                profile = profileForm.save(commit=False)
                user = request.user
                profile.user = user

                try:
                    profile.picture = request.FILES['picture']
                except:
                    pass

                profile.save()
                registered = True
        else:
            print profileForm.errors

        return index(request)

    else:
        profileForm = UserProfileForm(request.GET)

    context_dict = {}
    context_dict['profile'] = profileForm
    context_dict['registered'] = registered

    return render(request, 'rango/edit_profile.html', context_dict)

def user_profile(request, user_name):
     context_dict = {}

     otherUser = User.objects.get(username = user_name)
     context_dict['otherUser'] = otherUser

     try:
         otherProfile = UserProfile.objects.get(user = otherUser)
         context_dict['otherProfile'] = otherProfile
     except:
         pass

     return render(request, 'rango/user_profile.html', context_dict)

def users(request):

    users = User.objects.order_by('-email')
    context_dict = {'users': users}

    return render(request, 'rango/users.html', context_dict)

@login_required
def restricted(request):
    return render(request, "rango/restricted.html")

@login_required
def add_category(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.
            form.save(commit=True)

            # Now call the index() view.
            # The user will be shown the homepage.
            return index(request)
        else:
            # The supplied form contained errors - just print them to the terminal
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CategoryForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):

    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            if cat:
                page = form.save(commit=False)
                page.category = cat
                page.views = 0
                page.save()
                # probably better to use a redirect here.
                return category(request, category_name_slug)
        else:
            print form.errors
    else:
        form = PageForm()

    context_dict = {'form':form, 'category':cat, 'category_name_slug': category_name_slug}

    return render(request, 'rango/add_page.html', context_dict)

def index(request):
    # request.session.set_test_cookie()

    # Query the database for a list of ALL categories currently stored.
    # Order the pages by no. of likes in descending order.
    # Retrieve the top 5 only - or all if less than 5.
    # Place the list in our context_dict dictionary which will be passed to the template engine.
    category_list = Category.objects.all()
    page_list = Page.objects.order_by('-views')[:5]
    context_dict = {'categories': category_list, 'pages': page_list}

    # Get the number of visits to the site.
    # We use the COOKIES.get() function to obtain the visits cookie.
    # If the cookie exists, the value returned is casted to an integer.
    # If the cookie doesn't exist, we default to zero and cast that.
    visits = request.session.get('visits')
    if not visits:
        visits = 1
    reset_last_visit_time = False

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")

        if (datetime.now() - last_visit_time).days > 0:
            # ...reassign the value of the cookie to +1 of what it was before...
            visits = visits + 1
            # ...and update the last visit cookie, too.
            reset_last_visit_time = True
    else:
        # Cookie last_visit doesn't exist, so create it to the current date/time
        reset_last_visit_time = True

    if reset_last_visit_time:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = visits
    context_dict['visits'] = visits

    response = render(request, 'rango/index.html', context_dict)

    # Return response back to the user, updating any cookies that need changed.
    return response

def about(request):
#    context_dict = { 'boldmessage': "This tutorial has been put together by Jake Degiovanni, 2066890"}

    # If the visits session variable exists, take it and use it.
    # If it doesn't, we haven't visited the site to set the count to zero.
    if request.session.get('visits'):
        count = request.session.get('visits')
    else:
        count = 0

    # Remember to include the visit data
    return render(request, 'rango/about.html', {'visits': count})

    #return HttpResponse("Rango says here is the about page. "
    #                    "<p>This tutorial has been put together by Jake Degiovanni, 2066890</p>"
    #                    "<p><a href='/rango/'>Index</a></p>")

def category(request, category_name_slug):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}
    context_dict['result_list'] = None
    context_dict['query'] = None

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

            context_dict['result_list'] = result_list
            context_dict['query'] = query

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)
        context_dict['category_name'] = category.name

        # Retrieve all of the associated pages.
        # Note that filter returns >= 1 model instance.
        pages = Page.objects.filter(category=category).order_by('-views')

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
        context_dict['category_name_slug'] = category_name_slug
    except Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'rango/category.html', context_dict)

def search(request):

    result_list = []

    if request.method == 'POST':
        query = request.POST['query'].strip()

        if query:
            # Run our Bing function to get the results list!
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list': result_list})

