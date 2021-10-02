from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from datetime import datetime, timedelta

from transactions.models import Transaction
from transactions.services import get_exchanges, get_coins
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
                    user = User.objects.create(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
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
    queryset_list = Transaction.objects.order_by('purchasedDate').filter(userId=request.user.id)
    
    updateSoldQty(request)

    #total_trans = sum([t.total() for t in user_trans])

    paginator = Paginator(queryset_list, 5) #Shows 5 records per page
    page = request.GET.get('page')
    paged_trans = paginator.get_page(page)

    context = {
        'trans': paged_trans,
        #'total_trans': total_trans
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

        tran.save()

        # update soldqty


        messages.success(request, 'Transaction saved successfully.')
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
        tran.delete()

        messages.success(request, "Transaction deleted successfully.")
    else:
        messages.error(request, "There is an error deleting a transaction.")
    
    return redirect('accttransactions')


def updateSoldQty(request):
    queryset_list = Transaction.objects.order_by('coin','purchasedDate').filter(userId=request.user.id)
    queryset_bought = queryset_list.filter(transType__iexact="BUY")
    queryset_sold = queryset_list.filter(transType__iexact="SELL").values('coin').order_by('coin').annotate(total_soldQty=Sum('qty'))

    trans_list = []

    # Reset soldqty field on all buy transactions
    Transaction.objects.filter(transType="BUY").update(soldQty=0)

    for s in queryset_sold:
        sold_qty = s['total_soldQty']
        if sold_qty > 0:
            queryset_bought_by_coin = queryset_bought.filter(coin__iexact=s['coin']).order_by('purchasedDate')
            for b in queryset_bought_by_coin:
                print('coin')
                print(s['coin'])
                print('sold_qty')
                print(sold_qty)
                print('b.qty')
                print(b.qty)
                print('b.id')
                print(b.id)
                bought_tran = get_object_or_404(Transaction, pk=b.id)

                if sold_qty > b.qty:
                    bought_tran.soldQty = b.qty
                    bought_tran.save()
                    print('sold - if')
                    print(b.qty)
                    sold_qty = sold_qty - b.qty
                elif sold_qty > 0:
                    bought_tran.soldQty = sold_qty
                    bought_tran.save()
                    print('sold - else')
                    print(sold_qty)
                    sold_qty = 0
                    
                    

    print('bought:')
    print(queryset_bought)
    print('sold:')
    print(queryset_sold)

    return 1;