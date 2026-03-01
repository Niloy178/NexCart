from django.shortcuts import render, redirect
from django.contrib import messages, auth
from .forms import RegistrationForm
from .models import Account
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests

# varification main send
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage



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

            # USER Activation
            current_site = get_current_site(req)
            mail_subject = "Please activate your account."
            message = render_to_string("accounts/account_verification_email.html", {
                'user': account,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(account.pk)),
                'token': default_token_generator.make_token(account),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # Registration done goto login
            messages.success(req, 'We have send you a verification email. Confirm it to activate your account.')
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
            try:
                cart = Cart.objects.get(cart_id=_cart_id(req))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)
                    
                    # Getting all product veriations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation=item.variations.all()
                        product_variation.append(list(variation))
                    # get the cart items from the user to access his product variations
                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation=item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                        
                    # Check is common variaiton is available 
                    for pv in product_variation:
                        if pv in ex_var_list:
                            index=ex_var_list.index(pv)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()
                            
                            
                    # for item in cart_item:
                    #     item.user=user
                    #     item.save()
            except:
                pass

            auth.login(req, user)
            messages.success('You are now logged in.')
            url=req.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
                print(query)
                
                # next=/cart/checkout
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    next_page=params['next']
                    return redirect(next_page)        
            except:
                return redirect('dashboard')
               
        else:
            messages.error(req, 'Invalid Credentials')
            return redirect('login')
    return render(req, 'accounts/login.html')

@login_required(login_url="login")
def logout(req):
    auth.logout(req)
    messages.success(req, 'You are logged out.')
    return redirect('login')

def activate(req, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active=True
        user.save()
        messages.success(req, 'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(req, 'Invalid activation link.')
        return redirect('register')
        


# Dashboard function

def dashboard(req):



    return render(req, 'accounts/dashboard.html')

def forgot_password(req):


    if req.method == 'POST':
        email = req.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            
            # USER Activation
            current_site = get_current_site(req)
            mail_subject = "Reset password"
            message = render_to_string("accounts/reset_password_email.html", {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(req, 'Reset password mail has been sent to your email.')
            return redirect('login')


        else:
            messages.error(req, 'Account does not exist.')
            return redirect('forgot_password')
    
    return render(req, 'accounts/forgot_password.html')

def forgot_password_validate(req, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user=None

    if user is not None and default_token_generator.check_token(user, token):
        req.session['uid']=uid
        messages.success(req, 'Please reset your password.')
        return redirect('reset_password')
    else:
        messages.error(req, 'This link has been expired.')
        return redirect('login')
    
def reset_password(req):
    if req.method == 'POST':
        password = req.POST['password']
        confirm_password = req.POST['confirm_password']

        if password == confirm_password:
            uid = req.session.get('uid')
            user = Account.objects.get(id=uid)
            user.set_password(password)
            user.save()
            messages.success(req, 'Password reset successful.')
            return redirect('home')
        else:
            messages.error(req, 'Passwords do not matched.')
            return redirect('resetpassword')
    else:
        return render(req, 'accounts/reset_password.html')
    
