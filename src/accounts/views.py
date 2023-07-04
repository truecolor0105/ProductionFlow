import datetime, base64
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from .forms import RegisterForm
from flow.models import UserAccount


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()


            notes = "Goals\n\nHabit Reminders:\n1. Exercise first thing in the morning\n2. Keep water bottle filled at all times\n3. Meditate when tempted to snack or scroll IG\n4. Eat less carbs (more vegetables)\n5. Night routine 8pm (free to crash when tired)\n6. Spend less time on phone\n\nNotes:"
            ua = UserAccount()
            ua.user = user
            ua.notes = notes
            ua.key = (base64.b64encode((f'{user.id},{user.email}').encode('ascii'))).decode('ascii')
            ua.created = datetime.datetime.now()
            ua.creator = user
            ua.save()

            # get the username and password
            username = request.POST['username']
            password = request.POST['password1']
            # authenticate user then login
            login(request, authenticate(username=username, password=password))

            # views.api_create_company(request)
            # return redirect('/')
            return redirect('/accounts/review')
    else:
        form = RegisterForm()

    template_name = 'registration/register.html'
    context = {
        'form': form
    }
    return render(request, template_name, context)


# Create your views here.
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/')
    else:
        form = AuthenticationForm(request)
    context = {
        "form": form
    }
    return render(request, "registration/login.html", context)


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("/login/")
    return render(request, "registration/logout.html", {})


# User Review
@login_required(login_url='/accounts/login/')
def review(request):
    context = {
        "title": "Review"
    }
    return render(request, "flow/review.html", context)