import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Q, F
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password

from transactions.models import Transaction
from transactions.services import get_exchanges, get_coins, get_coin_latest_price
from transactions.choices import type_choices

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid credentials.")
            return redirect('login')
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    if request.method == 'POST':
        auth.logout(request)
        messages.success(request, "You are not logged out.")
        return redirect('index')
    
def register(request):
    if request.method == 'POST':
        # get form values
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # validations
        if password == password2:
            # check user
            if User.objects.filter(username=username).exists():
                messages.error(request, 'That username is already taken.')
                return redirect('register')

            else:
                if User.objects.filter(email=email).exists():
                    messages.error(request, 'That email is already been used.')
                    return redirect('register')
                else:
                    enc_password = make_password(password)
                    user = User.objects.create(username=username, password=enc_password, email=email, first_name=first_name, last_name=last_name)
                    user.save()
                    messages.success(request, 'You are now registered and ready to log in.') 
                    return redirect('login')
        else:
            messages.error(request, 'Passwords do not match.')    
            return redirect('register')


        #register user
        messages.error(request, 'Testing error message')
        return redirect('register')
    else:
        return render(request, 'accounts/register.html')

def dashboard(request):
    queryset_list = Transaction.objects.order_by('purchasedDate').filter(Q(userId=request.user.id) & Q(transType="BUY"))
    queryset_list = queryset_list.annotate(totalBought=F('qty') - F('soldQty'))
    queryset_list = queryset_list.filter(totalBought__gt=0)
          
    # Get the latest price per coin
    coin_list = queryset_list.order_by('coin').values('coin').distinct()
    
    trans_latestprice_list = []
    grandtotal_cost = 0
    grandtotal_value = 0
    grandtotal_gainloss = 0

    for c in coin_list:
        #get coin latest price
        coin_price = get_coin_latest_price(c['coin'])
        
        total_qty = 0
        total_cost = 0
        total_value = 0
        total_gainloss = 0

        for cl in queryset_list:
            if c['coin'] == cl.coin:
                total_qty = total_qty + float(cl.totalBought)
                total_cost = total_cost + (float(cl.priceAtBought) * float(cl.totalBought)) + float(cl.fees)
                total_value = total_value + float(coin_price) * float(cl.totalBought)
                total_gainloss = total_gainloss + (total_value - total_cost)
        
        grandtotal_cost = grandtotal_cost + total_cost
        grandtotal_value = grandtotal_value + total_value
        grandtotal_gainloss = grandtotal_gainloss + total_gainloss
        trans_latestprice_list.append(( c['coin'], total_qty, coin_price, total_cost, total_value, total_gainloss ))

    paginator = Paginator(trans_latestprice_list, 5) #Shows 5 records per page
    page = request.GET.get('page')
    paged_trans = paginator.get_page(page)

    context = {
        'trans': paged_trans,
        'grandtotal_cost': grandtotal_cost,
        'grandtotal_value': grandtotal_value,
        'grandtotal_gainloss': grandtotal_gainloss
    }

    return render(request, 'accounts/dashboard.html', context)

def accttransactions(request):

    queryset_list = Transaction.objects.order_by('-purchasedDate').filter(userId=request.user.id)
    queryset_total = queryset_list.count
    filter_qrystring = ""
    
    # Search exchange name
    if 'exchange' in request.GET:
        exchange = request.GET['exchange']
        filter_qrystring = filter_qrystring + "&exchange=" + exchange
        if exchange:
            queryset_list = queryset_list.filter(exchange__icontains=exchange)
    
    #Search coin symbol
    if 'coin' in request.GET:
        coin = request.GET['coin']
        filter_qrystring = filter_qrystring + "&coin=" + coin
        if coin:
            queryset_list = queryset_list.filter(coin__icontains=coin)

    #Search transaction type
    if 'transType' in request.GET:
        transType = request.GET['transType']
        filter_qrystring = filter_qrystring + "&transType=" + transType
        if transType and transType != "ALL":
            queryset_list = queryset_list.filter(transType__iexact=transType)

    #Search purchased date range
    if 'purchasedDateFrom' in request.GET and 'purchasedDateTo' in request.GET:
        purchasedDateFrom = request.GET['purchasedDateFrom']
        purchasedDateTo = request.GET['purchasedDateTo']
        filter_qrystring = filter_qrystring + "&purchasedDateFrom=" + purchasedDateFrom + "&purchasedDateTo=" + purchasedDateTo
        print(purchasedDateFrom)
        if purchasedDateFrom and purchasedDateTo and purchasedDateFrom == purchasedDateTo:
            queryset_list = queryset_list.filter(purchasedDate__contains=purchasedDateFrom)
        elif purchasedDateFrom and not purchasedDateTo:
            queryset_list = queryset_list.filter(purchasedDate__gte=purchasedDateFrom)
        elif not purchasedDateFrom and purchasedDateTo:
            filterDateTo = datetime.strptime(purchasedDateTo, "%Y-%m-%d").date() + timedelta(1)
            queryset_list = queryset_list.filter(purchasedDate__lte=filterDateTo)
        elif purchasedDateFrom and purchasedDateTo:
            queryset_list = queryset_list.filter(purchasedDate__range=(purchasedDateFrom, purchasedDateTo))

    if 'orderBy' in request.GET:
        orderBy = request.GET['orderBy']
        if orderBy:
            queryset_list = queryset_list.order_by(orderBy)

    paginator = Paginator(queryset_list, 5) #Shows 5 records per page
    page = request.GET.get('page')
    paged_trans = paginator.get_page(page)

    context = {
        'trans': paged_trans,
        'type_choices': type_choices,
        'values' : request.GET,
        'filter_qrystring': filter_qrystring,
        'queryset_total': queryset_total,
        'filter_queryset_total': queryset_list.count
    }

    return render(request, 'accounts/transactions.html', context)

def accttransaction(request, tran_id):
    #save transaction
    if request.method == "POST":

        userId = request.POST['userId']
        purchasedDate = request.POST['purchasedDate']
        coin = request.POST['coin']
        exchange = request.POST['exchange']
        transType = request.POST['transType']
        priceAtBought = request.POST['priceAtBought']
        qty = request.POST['qty']
        fees = request.POST['fees']
        notes = request.POST['notes']
        selTranId = int(request.POST['id'])

        if selTranId > 0:
            tran = get_object_or_404(Transaction, pk=selTranId)
            tran.purchasedDate = purchasedDate
            tran.coin = coin
            tran.exchange = exchange
            tran.transType = transType
            tran.priceAtBought = priceAtBought
            tran.qty = qty
            tran.fees = fees
            tran.notes = notes
        
        else:
            tran = Transaction(exchange=exchange, coin=coin, transType=transType, priceAtBought=priceAtBought, 
                purchasedDate=purchasedDate, qty=qty, fees=fees, notes=notes, userId=userId)
        
        isValid = 1
        if transType == "SELL":
            # check is sell is possible
            isValid = checkCoinExchangeToSell(request)

        if isValid == 1:
            tran.save()

            if transType == "SELL":
                # Update sold qty
                updateSoldQty(request)

            messages.success(request, 'Transaction saved successfully.')
            return redirect('accttransactions')

        else:
            messages.error(request, 'Error selling a coin.')
            return redirect('accttransactions')

    else:

        if tran_id > 0:
            tran = get_object_or_404(Transaction, pk=tran_id)
        else:
            tran = Transaction()
            tran.purchasedDate = timezone.now()

        context = {
            'exchanges': get_exchanges(),
            'coins': get_coins(),
            'type_choices': type_choices,
            'tran': tran,
            'tran_id': tran_id
        }
        
        return render(request, 'accounts/transaction.html', context)

def accttransactiondelete(request, tran_id):

    #delete transaction
    if tran_id and int(tran_id) > 0:
        tran = get_object_or_404(Transaction, pk=int(tran_id))

        #check is delete is allowed
        isValid = checkCoinExchangeToDelete(request.user.id, tran)

        if isValid == 1:
            tran.delete()

            # Update sold qty
            updateSoldQty(request)

            messages.success(request, "Transaction deleted successfully.")

        else:
            messages.error(request, 'Error deleting a coin.')
            return redirect('accttransactions')
    else:
        messages.error(request, "There is an error deleting a transaction.")
    
    return redirect('accttransactions')

def checkCoinExchangeToSell(request):

    coin = request.POST['coin']
    exchange = request.POST['exchange']

    # making sure user has enough coin qty to sell
    queryset_list = Transaction.objects.filter(Q(userId=request.user.id) & Q(transType__iexact="BUY") & Q(coin__iexact=coin) & Q(exchange__iexact=exchange))
    queryset_list = queryset_list.annotate(totalBought=F('qty') - F('soldQty'))
    queryset_list = queryset_list.filter(totalBought__gte=0)
    
    if len(queryset_list) > 0:
        return 1
    else:
        return 0;

def checkCoinExchangeToDelete(user_id, tran):

    if tran.transType == "BUY":
        coin = tran.coin
        exchange = tran.exchange
        
        # check if delete is possible on 'buy' transaction
        # making sure that one user is deleting has not been sold
        queryset_list = Transaction.objects.filter(Q(userId=user_id) & Q(transType__iexact="BUY") & Q(coin__iexact=coin) & Q(exchange__iexact=exchange))
        queryset_list = queryset_list.annotate(total=F('qty') - F('soldQty') - tran.qty)
        queryset_list = queryset_list.filter(total__gte=0)
          
        if len(queryset_list) > 0:
            return 1
        else:
            return 0
    else:
        return 1

def updateSoldQty(request):
    queryset_list = Transaction.objects.order_by('coin','exchange','purchasedDate').filter(userId=request.user.id)
    queryset_bought = queryset_list.filter(transType__iexact="BUY")
    queryset_sold = queryset_list.filter(transType__iexact="SELL").values('coin','exchange').order_by('exchange','coin').annotate(total_soldQty=Sum('qty'))
  
    # Reset soldqty field on all buy transactions
    Transaction.objects.filter(Q(transType="BUY") & Q(userId=request.user.id)).update(soldQty=0)

    # Update bought coin's qty with sold qty
    for s in queryset_sold:
        sold_qty = s['total_soldQty']
                
        if sold_qty > 0:
            queryset_bought_by_coin = queryset_bought.filter(Q(coin__iexact=s['coin']) & Q(exchange__iexact=s['exchange'])).order_by('coin','exchange','purchasedDate')
            for b in queryset_bought_by_coin:
                bought_tran = get_object_or_404(Transaction, pk=b.id)
                if sold_qty > b.qty:
                    bought_tran.soldQty = b.qty
                    bought_tran.save()
                    sold_qty = sold_qty - b.qty
                elif sold_qty > 0:
                    bought_tran.soldQty = sold_qty
                    bought_tran.save()
                    sold_qty = 0
                    
    return 1