"""salon URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from service import views
from book import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from service.views import SignUpView, activate

urlpatterns = [
    path('GHB/', admin.site.urls),
    path('', views.index, name='index'),
    path('booking', views.booking, name='booking'),
    path('booking-date', views.bookingDate, name='bookingDate'),
    path('none-user-booking-date', views.noneUserBookingDate, name='noneUserBookingDate'),
    path('booking-time', views.bookingTime, name='bookingTime'),
    path('none-user-booking-time', views.noneUserBookingTime, name='noneUserBookingTime'),
    path('user-panel', views.userPanel, name='userPanel'),
    path('user-update/<int:id>', views.userUpdate, name='userUpdate'),
    path('user-update-submit/<int:id>', views.userUpdateSubmit, name='userUpdateSubmit'),
    path('staff-panel', views.staffPanel, name='staffPanel'),
    path('staff-lock-date', views.staffLockDate, name='staffLockDate'), 
    path('accounts/login/', auth_views.LoginView.as_view()),
    path('signup/', SignUpView, name='signup'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('payment/', views.payment, name='payment'),
    path('none-user-payment/', views.noneUserPayment, name='noneUserPayment'),
    path('lock-date/', views.staffLockDate, name='lockDate'),
    path('payment-update/<int:id>', views.paymentUpdate, name='paymentUpdate'),

]

urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)