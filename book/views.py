from django.shortcuts import render, redirect
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import *
from django.contrib import messages
from django.conf import settings
from service.models import *
import stripe


def index(request):
    return render(request, "index.html")

def booking(request):

    braid = Braid.objects.all()
    twist = Twist.objects.all()
    other_service = Other_service.objects.all()
    crochet = Crochet.objects.all()
    natural_hair = Natural_hair.objects.all()
    

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
        deposit = request.POST.get('amount')
        request.session['amount'] = deposit
        date = dayToWeekday(day)

        if service != None:
            if day <= maxDate and day >= minDate:
                if date == 'Monday' or date == 'Tuesday' or date == 'Wednesday' or date == 'Thursday' or date == 'Friday' or date == 'Saturday' or date == 'Sunday':
                    if Appointment.objects.filter(day=day).count() < 3:
                        if Appointment.objects.filter(day=day, time=time).count() < 1:
                            if deposit:
                                return redirect('payment')
                            else:
                                messages.error(request, "Enter amount to deposit!")
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
    service = request.session.get('service')
    day = request.session.get('day')
    price = request.session.get('price')
    time = request.session.get('time')
    deposit = request.session.get('amount')
    deposit_int = int(deposit) * 100
    print(deposit_int)

    if request.method == 'POST':
    
        charge = stripe.Charge.create(
            amount = deposit_int,
            currency='usd',
            description='payment successful',
            source=request.POST['stripeToken']
        )

        AppointmentForm = Appointment.objects.get_or_create(
            user = user,
            service = service,
            day = day,
            time = time,
            price = price,
            deposit = deposit,

        )
        messages.success(request, f"{user.username} your booking was succesful.")
        return redirect('userPanel')
    return render(request, 'payment.html', {
        'Key':Key,
        'service':service,
        'day':day,
        'time':time,
        'price':price,
        'deposit':deposit,
        'deposit_int':deposit_int,
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
        update_count = request.POST.get('update_count')
    
        #Store day in django session:
        request.session['day'] = day
        request.session['update_count'] = update_count

        return redirect('userUpdateSubmit', id=id)

    return render(request, 'userUpdate.html', {
            'weekdays':weekdays,
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
                        messages.success(request, "Appointment Updated!")
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
    prev_deposit = appointment.deposit
    price = appointment.price
    balance = price - prev_deposit
    if prev_deposit < price:
        deposit = price - prev_deposit
        current_deposit = deposit * 100
    
    if request.POST:
        deposit_update = balance + prev_deposit
        charge = stripe.Charge.create(
                amount = current_deposit,
                currency='usd',
                description='payment successful',
                source=request.POST['stripeToken']
            )

        AppointmentForm = Appointment.objects.filter(pk=id).update(
                        user = user,
                        deposit = deposit_update,
                    )
        messages.success(request, f"Your balance payment of ${balance} was succesfull!")
        return redirect('userPanel')
    return render(request, 'paymentUpdate.html', {
        'current_deposit':current_deposit,
         'Key':Key,
         'appointment':appointment,
         'balance': balance,
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
