from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import send_mail
from service.forms import RegisterForm
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from service.token import token_generator
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
# Create your views here.


def SignUpView(request):
    
    if request.POST:
        email = request.POST['email']
        form = RegisterForm(request.POST)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered with an existing account, please use another Email address')
            return redirect('signup')
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            mail_subject = "Activate your account."
            message = render_to_string("email/activate_account.html", {
            'user': user.first_name,
            'domain': get_current_site(request).domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': token_generator.make_token(user),
            'protocol': 'https' if request.is_secure() else 'http'
            })

            send_mail(
                mail_subject,
                'Here is the message',
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=message,
                fail_silently=False
                )
            if send_mail:
                messages.success(request, f"A mail with verification link has been sent to {user.email}")
            else:
                messages.error(request, f'There was an issue sending mail to {user.email}')

            return redirect('index')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def activateEmail(request, user, to_email):
    mail_subject = "Activate your account."
    message = render_to_string("activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': token_generator.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send:
        messages.success(request, f"A mail with verification link has been sent to {to_email}")
    else:
        messages.error(request, f"There was an issue sending mail to {to_email}")


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    
    except:
        user = None

    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('login')

    else:
        messages.error(request, "Activation link is invalid")
    return redirect('index')

class CheckEmailView(TemplateView):
    template_name = 'check_email.html'

class SuccessView(TemplateView):
    template_name = 'successful.html'