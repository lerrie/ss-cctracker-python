from django.shortcuts import render
from .services import get_exchanges

from .models import Transaction

def index(request):
    trans = Transaction.objects.all()

    context = {
        'trans': trans
    }

    return render(request, 'transactions/transactions.html', context)

def transaction(request):
    return render(request, 'transactions/transaction.html')


