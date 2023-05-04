from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from service.models import *
import stripe


def index(request):
    return render(request, "index.html")

def booking(request):

    braid = Braid.objects.all().order_by('name')
    twist = Twist.objects.all().order_by('name')
    other_service = Other_service.objects.all().order_by('name')
    crochet = Crochet.objects.all().order_by('name')
    natural_hair = Natural_hair.objects.all().order_by('name')
    

    if request.method == 'POST':
        service = request.POST.get('service')
        price = request.POST.get('price')
        #day = request.POST.get('day')
    
        if service == None:
            messages.success(request, "Please Select A Service!")
            return redirect('booking')

        #Store day and service in django session:
        #request.session['day'] = day
        request.session['service'] = service
        request.session['price'] = price

        return redirect('bookingDate')


    return render(request, 'booking.html', {
            'braid': braid,
            'twist': twist,
            'natural_hair': natural_hair,
            'crochet': crochet,
            'other_service': other_service
        })


def bookingDate(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    #Only show the Appointments 21 days from today
    lockdays = LockDate.objects.all()

    #lockday = list(lockdate)
    
    #Calling 'validWeekday' Function to Loop days you want in the next 60 days:
    weekdays = validWeekday(60)
    #Only show the days that are not full:
    
    
    if lockdays:
        validateWeekdays = removeDate()

    else:
        validateWeekdays = isWeekdayValid(weekdays)


    if request.method == 'POST':
        day = request.POST.get('day')

        if day == None:
            messages.success(request, "Please Select A Date!")
            return redirect('bookingDate')

        #Store day and in django session:
        request.session['day'] = day
        
        return redirect('bookingTime')
        
    return render(request, 'bookingDate.html', {'weekdays':weekdays, 'validateWeekdays':validateWeekdays})

@login_required
def bookingTime(request):
    date = datetime.now().date()
    date_str = date.strftime('%Y-%m-%d')
    now = datetime.now()
    day = request.POST.get('day')
    day = request.session.get('day')
    
    if day == date_str and now.hour >= 7:

        times = [
            "2 PM"
        ]

    else:
        times = [
            "8 AM", "2 PM"
        ] 

    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=60)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    #Get stored data from django session:
    
    service = request.session.get('service')
    price = request.session.get('price')
    
    #Only show the time of the day that has not been selected before:
    hour = checkTime(times, day)
    if request.method == 'POST':
        time = request.POST.get("time")
        request.session['time'] = time
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Tuesday' or date == 'Wednesday' or date == 'Thursday' or date == 'Friday' or date == 'Saturday' or date == 'Sunday':
                    if Appointment.objects.filter(day=day).count() < 3:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            return redirect('payment')
                        else:
                            messages.error(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.error(request, "The Selected Day Is Full!")
                else:
                    messages.error(request, "The Selected Date Is Incorrect")
            else:
                    messages.error(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.error(request, "Please Select A Service!")


    return render(request, 'bookingTime.html', {
        'times':hour,
        'now': now,
        'day': day,
        'price': price, 
    })

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def payment(request):
    user = request.user
    Key = settings.STRIPE_PUBLISHABLE_KEY
    s_key = settings.STRIPE_SECRET_KEY
    service = request.session.get('service')
    day = request.session.get('day')
    price = request.session.get('price')
    time = request.session.get('time')
    #deposit = request.session.get('amount')
    #deposit_int = int(deposit) * 100

    if request.method == 'POST':
        amount = int(request.POST['amount'])
        
        try:
    
            customer = stripe.Customer.create(
                email = request.POST.get('email'),
                name = request.POST.get('full_name'),
                description = "Hair Booking",
                source=request.POST['stripeToken'],
            )

        except stripe.error.CardError as e:
            messages.error(request, 'There was an error charging your card, ensure you have sufficient funds')
            return redirect('payment')

        except stripe.error.RateLimitError as e:
            messages.error(request, 'Rate Error')
            return redirect('payment')

        except stripe.error.InvalidRequestError as e:
            messages.error(request, 'Invalid requestor!')
            return redirect('payment')

        except stripe.error.AuthenticationError as e:
            messages.error(request, 'Invalid API auth')
            return redirect('payment')

        except stripe.error.StripeError as e:
            messages.error(request, 'Stripe Error')
            return redirect('payment')

        except Exception as e:
            messages.error(request, 'Error paying with your card at the moment')
            return redirect('payment')

        charge = stripe.Charge.create(
            customer=customer,
            amount = amount * 100,
            currency = 'usd',
            description='Hair Booking',
        )

        AppointmentForm = Appointment.objects.get_or_create(
                user = user,
                service = service,
                day = day,
                time = time,
                price = price,
                deposit = amount,
            )

        transRetrive = stripe.Charge.retrieve(
            charge["id"],
            api_key = settings.STRIPE_SECRET_KEY
            )
            
        charge.save() # Uses the same API Key.

        messages.success(request, f"{user.username} your booking was succesful.")

        try:
            mail_subject = "Your Booking was successful!"
            message = render_to_string("email/booking_confirmation.html", {
            'user': user.first_name,
            'email': user.email,
            'service': service,
            'day': day,
            'time': time,
            'price': price,
            'deposit': amount,
            })

            send_mail(
                mail_subject,
                'Here is the message',
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=message,
                fail_silently=False
                )
        except:
            messages.error(request, 'Failed to send confirmation Mail')

        return redirect('userPanel')
    return render(request, 'payment.html', {
        'Key':Key,
        'service':service,
        'day':day,
        'time':time,
        'price':price,
    })

@login_required
def userPanel(request):
    user = request.user
    now = datetime.now().date()

    appointments = Appointment.objects.filter(user=user,).order_by('-day', 'time')
    return render(request, 'userPanel.html', {
        'user':user,
        'appointments':appointments,
        'now': now,
    })
    
@login_required
def userUpdate(request, id):
    appointment = Appointment.objects.get(pk=id)
    service = appointment.service
    deposit = appointment.deposit
    price = appointment.price
    updated_count = appointment.update_count
    userdatepicked = appointment.day
    #Copy  booking:
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    date = datetime.now().date()
    date_str = date.strftime('%Y-%m-%d')
    now = datetime.now()
    
    
    #24h if statement in template:
    delta24 = (userdatepicked).strftime('%Y-%m-%d') >= (today + timedelta(days=1)).strftime('%Y-%m-%d')
    #Calling 'validWeekday' Function to Loop days you want in the next 21 days:
    weekdays = validWeekday(60)

    #Only show the days that are not full:
    validateWeekdays = isWeekdayValid(weekdays)

    messages.success(request, "Note! you can only update this appointment once")

    if request.method == 'POST':
        day = request.POST.get('day')
        day = request.POST.get('day')
        service = request.POST.get('service')
        update_count = request.POST.get('update_count')
    
        #Store day in django session:
        request.session['day'] = day
        request.session['service'] = service
        request.session['update_count'] = update_count

        return redirect('userUpdateSubmit', id=id)

    return render(request, 'userUpdate.html', {
            'weekdays':weekdays,
            'service':service, 
            'validateWeekdays':validateWeekdays,
            'delta24': delta24,
            'id': id,
            'updated_count': updated_count,
        })

@login_required
def userUpdateSubmit(request, id):
    user = request.user
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    date = datetime.now().date()
    date_str = date.strftime('%Y-%m-%d')
    now = datetime.now()
    day = request.POST.get('day')
    day = request.session.get('day')
    service = request.session.get('service')
    update_count = int(request.session['update_count']) 
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=60)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    day = request.session.get('day')

    if day == date_str and now.hour >= 7:

        times = [
            "2 PM"
        ]

    else:
        times = [
            "8 AM", "2 PM"
        ]
    
    #Only show the time of the day that has not been selected before and the time he is editing:
    hour = checkEditTime(times, day, id)
    appointment = Appointment.objects.get(pk=id)
    userSelectedTime = appointment.time
    if request.method == 'POST':
        time = request.POST.get("time")
        date = dayToWeekday(day)
        update_count += 1

        if day <= maxDate and day >= minDate:
            if date == 'Monday' or date == 'Tuesday' or date == 'Wednesday' or date == 'Thursday' or date == 'Friday' or date == 'Saturday' or date == 'Sunday':
                if Appointment.objects.filter(day=day).count() < 3:
                    if Appointment.objects.filter(day=day, time=time).count() < 1 or userSelectedTime == time:
                        AppointmentForm = Appointment.objects.filter(pk=id).update(
                            user = user,
                            day = day,
                            time = time,
                            update_count = update_count,
                        )
                        try: 
                            messages.success(request, "Appointment Updated!")
                            mail_subject = "Your Booking has been updated!"
                            message = render_to_string("email/update_confirmation_email.html", {
                            'user': user.first_name,
                            'email': user.email,
                            'service': service,
                            'day': day,
                            'time': time,
                            })

                            send_mail(
                                mail_subject,
                                'Here is the message',
                                settings.EMAIL_HOST_USER,
                                [user.email],
                                html_message=message,
                                fail_silently=False
                                )
                        except:
                            messages.error(request, 'Failed to send confirmation Mail')
                        return redirect('userPanel')
                    else:
                        messages.error(request, "The Selected Time Has Been Reserved Before!")
                else:
                    messages.error(request, "The Selected Day Is Full!")
            else:
                messages.error(request, "The Selected Date Is Incorrect")
        else:
                messages.error(request, "The Selected Date Isn't In The Correct Time Period!")

    return render(request, 'userUpdateSubmit.html', {
        'times':hour,
        'id': id,
        'update_count': update_count
    })

@login_required
def paymentUpdate(request, id):
    user = request.user
    Key = settings.STRIPE_PUBLISHABLE_KEY
    appointment = Appointment.objects.get(pk=id)
    service = appointment.service
    prev_deposit = appointment.deposit
    price = appointment.price
    balance = price - prev_deposit

    if request.method == 'POST':
        deposit_update = balance + prev_deposit
        
        try:
    
            customer = stripe.Customer.create(
                email = request.POST.get('email'),
                name = request.POST.get('full_name'),
                description = "Hair Booking",
                source=request.POST['stripeToken'],
            )

        except stripe.error.CardError as e:
            messages.error(request, 'There was an error charging your card, ensure you have sufficient funds')
            return redirect('payment')

        except stripe.error.RateLimitError as e:
            messages.error(request, 'Rate Error')
            return redirect('payment')

        except stripe.error.InvalidRequestError as e:
            messages.error(request, 'Invalid requestor!')
            return redirect('payment')

        except stripe.error.AuthenticationError as e:
            messages.error(request, 'Invalid API auth')
            return redirect('payment')

        except stripe.error.StripeError as e:
            messages.error(request, 'Stripe Error')
            return redirect('payment')

        except Exception as e:
            messages.error(request, 'Error paying with your card at the moment')
            return redirect('payment')

        charge = stripe.Charge.create(
                customer=customer,
                amount = balance * 100,
                currency='usd',
                description='Hair Booking',
            )

        AppointmentForm = Appointment.objects.filter(pk=id).update(
                        user = user,
                        deposit = deposit_update,
                    )
        transRetrive = stripe.Charge.retrieve(
            charge["id"],
            api_key = settings.STRIPE_SECRET_KEY
            )
            
        charge.save() # Uses the same API Key.
        messages.success(request, f"Your balance payment of ${balance} was succesfull!")

        try:
            mail_subject = "Your Booking was successful!"
            message = render_to_string("email/payment_update_email.html", {
            'user': user.first_name,
            'email': user.email,
            'service': service,
            'price': price,
            'balance': balance,
            })

            send_mail(
                mail_subject,
                'Here is the message',
                settings.EMAIL_HOST_USER,
                [user.email],
                html_message=message,
                fail_silently=False
                )
        except:
            messages.error(request, 'Failed to send confirmation Mail')
        
        return redirect('userPanel')
    return render(request, 'paymentUpdate.html', {
        'current_deposit':balance,
         'Key':Key,
         'appointment':appointment,
         'balance': balance,
         'user':user,
         })


def staffPanel(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    #Only show the Appointments 21 days from today
    items = Appointment.objects.filter(day__range=[minDate, maxDate]).order_by('day', 'time')

    return render(request, 'staffPanel.html', {
        'items':items,
    })

def staffLockDate(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=60)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    lockdate = LockDate.objects.filter(date__range=[minDate, maxDate]).order_by('date')
    lockdays = LockDate.objects.all()
    weekdays = validWeekday(60)
    if lockdays:
        validateWeekdays = removeDate()

    else:
        validateWeekdays = isWeekdayValid(weekdays)

    if request.POST:
        date_id = request.POST.get('date_id')
        lockdate = request.POST.get('lockdate')
        if date_id:
            unlockdate = LockDate.objects.get(id=date_id)
            unlockdate.delete()
            messages.success(request, f"{unlockdate} unlocked succesfully")
            return redirect('staffLockDate')
        if lockdate:
            lockdate = LockDate(date=lockdate)
            lockdate.save()
            messages.success(request, f"{lockdate} locked succesfully")
            return redirect('staffLockDate')

    context = {
        'lockdate': lockdate,
        'validateWeekdays': validateWeekdays
    }
    return render(request, 'staffLockDate.html', context)


def dayToWeekday(x):
    z = datetime.strptime(x, "%Y-%m-%d")
    y = z.strftime('%A')
    return y

def validWeekday(days):
    #Loop days you want in the next 60 days:
    today = datetime.now()
    weekdays = []
    for i in range (0, days):
        x = today + timedelta(days=i)
        y = x.strftime('%A')
        if y == 'Monday' or y == 'Tuesday' or y == 'Wednesday' or y == 'Thursday' or y == 'Friday' or y == 'Saturday' or y == 'Sunday':
            weekdays.append(x.strftime('%Y-%m-%d'))
    return weekdays
    
def isWeekdayValid(k):
    validateWeekdays = []
    for j in k:
        if Appointment.objects.filter(day=j).count() < 2:
            validateWeekdays.append(j)
    return validateWeekdays

def checkTime(times, day):
    #Only show the time of the day that has not been selected before:
    x = []
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1:
            x.append(k)
    return x

def checkEditTime(times, day, id):
    #Only show the time of the day that has not been selected before:
    x = []
    appointment = Appointment.objects.get(pk=id)
    time = appointment.time
    for k in times:
        if Appointment.objects.filter(day=day, time=k).count() < 1 or time == k:
            x.append(k)
    return x

def lockDate():
    lockdate = LockDate.objects.values_list('date', flat=True)
    lockdates = [d.strftime('%Y-%m-%d') for d in lockdate]
    if lockdates:
        return lockdates

def removeDate():
    lockdate = LockDate.objects.values_list('date', flat=True)
    lockdates = [d.strftime('%Y-%m-%d') for d in lockdate]

    #Calling 'validWeekday' Function to Loop days you want in the next 60 days:
    weekdays = validWeekday(60)
    #Only show the days that are not full:

    validateWeekdays = isWeekdayValid(weekdays)
    if lockdates:
        validateWeekdays = [n for n in validateWeekdays if n not in lockdates]
        return validateWeekdays


def noneUserBookingDate(request):
    today = datetime.today()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=21)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime
    #Only show the Appointments 21 days from today
    lockdays = LockDate.objects.all()

    #lockday = list(lockdate)
    
    #Calling 'validWeekday' Function to Loop days you want in the next 60 days:
    weekdays = validWeekday(60)
    #Only show the days that are not full:
    
    
    if lockdays:
        validateWeekdays = removeDate()

    else:
        validateWeekdays = isWeekdayValid(weekdays)


    if request.method == 'POST':
        day = request.POST.get('day')

        if day == None:
            messages.success(request, "Please Select A Date!")
            return redirect('noneUserBookingDate')

        #Store day and in django session:
        request.session['day'] = day
        
        return redirect('noneUserBookingTime')
        
    return render(request, 'noneUserBookingDate.html', {'weekdays':weekdays, 'validateWeekdays':validateWeekdays})

def noneUserBookingTime(request):
    date = datetime.now().date()
    date_str = date.strftime('%Y-%m-%d')
    now = datetime.now()
    day = request.POST.get('day')
    day = request.session.get('day')
    
    if day == date_str and now.hour >= 7:

        times = [
            "2 PM"
        ]

    else:
        times = [
            "8 AM", "2 PM"
        ] 

    today = datetime.now()
    minDate = today.strftime('%Y-%m-%d')
    deltatime = today + timedelta(days=60)
    strdeltatime = deltatime.strftime('%Y-%m-%d')
    maxDate = strdeltatime

    #Get stored data from django session:
    
    service = request.session.get('service')
    price = request.session.get('price')
    
    #Only show the time of the day that has not been selected before:
    hour = checkTime(times, day)
    if request.method == 'POST':
        time = request.POST.get("time")
        request.session['time'] = time
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Tuesday' or date == 'Wednesday' or date == 'Thursday' or date == 'Friday' or date == 'Saturday' or date == 'Sunday':
                    if Appointment.objects.filter(day=day).count() < 3:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            return redirect('noneUserPayment')
                        else:
                            messages.error(request, "The Selected Time Has Been Reserved Before!")
                    else:
                        messages.error(request, "The Selected Day Is Full!")
                else:
                    messages.error(request, "The Selected Date Is Incorrect")
            else:
                    messages.error(request, "The Selected Date Isn't In The Correct Time Period!")
        else:
            messages.error(request, "Please Select A Service!")


    return render(request, 'noneUserBookingTime.html', {
        'times':hour,
        'now': now,
        'day': day,
        'price': price, 
    })

def noneUserPayment(request):
    Key = settings.STRIPE_PUBLISHABLE_KEY
    s_key = settings.STRIPE_SECRET_KEY
    service = request.session.get('service')
    day = request.session.get('day')
    price = request.session.get('price')
    time = request.session.get('time')
    #deposit = request.session.get('amount')
    #deposit_int = int(deposit) * 100

    if request.method == 'POST':
        amount = int(request.POST['amount'])
        full_name = request.POST['full_name']
        email = request.POST['email']
        
        try:
    
            customer = stripe.Customer.create(
                email = request.POST.get('email'),
                name = request.POST.get('full_name'),
                description = "Hair Booking",
                source=request.POST['stripeToken'],
            )

        except stripe.error.CardError as e:
            messages.error(request, 'There was an error charging your card, ensure you have sufficient funds')
            return redirect('noneUserPayment')

        except stripe.error.RateLimitError as e:
            messages.error(request, 'Rate Error')
            return redirect('noneUserPayment')

        except stripe.error.InvalidRequestError as e:
            messages.error(request, 'Invalid requestor!')
            return redirect('noneUserPayment')

        except stripe.error.AuthenticationError as e:
            messages.error(request, 'Invalid API auth')
            return redirect('noneUserPayment')

        except stripe.error.StripeError as e:
            messages.error(request, 'Stripe Error')
            return redirect('noneUserPayment')

        except Exception as e:
            messages.error(request, 'Error paying with your card at the moment')
            return redirect('noneUserPayment')

        charge = stripe.Charge.create(
            customer=customer,
            amount = amount * 100,
            currency = 'usd',
            description='Hair Booking',
        )

        AppointmentForm = Appointment.objects.get_or_create(
                name = full_name,
                service = service,
                day = day,
                time = time,
                price = price,
                deposit = amount,
            )

        transRetrive = stripe.Charge.retrieve(
            charge["id"],
            api_key = settings.STRIPE_SECRET_KEY
            )
            
        charge.save() # Uses the same API Key.

        messages.success(request, f"{full_name} your booking was succesful.")

        try:
            mail_subject = "Your Booking was successful!"
            message = render_to_string("email/booking_confirmation.html", {
            'user': full_name,
            'email': email,
            'service': service,
            'day': day,
            'time': time,
            'price': price,
            'deposit': amount,
            })

            send_mail(
                mail_subject,
                'Here is the message',
                settings.EMAIL_HOST_USER,
                [email],
                html_message=message,
                fail_silently=False
                )
        except:
            messages.error(request, 'Failed to send confirmation Mail')

        return redirect('index')
    return render(request, 'noneUserPayment.html', {
        'Key':Key,
        'service':service,
        'day':day,
        'time':time,
        'price':price,
    }) 