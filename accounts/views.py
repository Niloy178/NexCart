from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .forms import RegistrationForm
from .models import Account
from django.contrib.auth.decorators import login_required
# Create your views here.



def register(req):
    # Form submission
    if req.method=='POST':
        form = RegistrationForm(req.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            
            username = email.split('@')[0]


            account = Account.objects.create_user(first_name=first_name, last_name=last_name,username=username, email=email, password=password)
            account.phone_number=phone_number
            account.save()
            messages.success(req, 'Registration successful.')
            return redirect('register')
    else:
        # HTML form creating for taking user input
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    return render(req, 'accounts/register.html', context)


# User login functionalities
def login(req):
    if req.method=='POST':
        email = req.POST['email']
        password = req.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(req, user)
            return redirect('home')
        else:
            messages.error(req, 'Invalid Credentials')
            return redirect('login')



    return render(req, 'accounts/login.html')

@login_required(login_url="login")
def logout(req):
    auth.logout(req)
    messages.success(req, 'You are logged out.')
    return redirect('login')