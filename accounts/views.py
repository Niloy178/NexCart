from django.shortcuts import render
from .forms import RegistrationForm
from .models import Account
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
    else:
        # HTML form creating for taking user input
        form = RegistrationForm()
    
    context = {
        'form': form,
    }
    return render(req, 'accounts/register.html', context)

def login(req):
    return render(req, 'accounts/login.html')

def logout(req):
    pass