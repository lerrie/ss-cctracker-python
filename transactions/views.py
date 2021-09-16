from django.shortcuts import render

def index(request):
    return render(request, 'transactions/transactions.html')

def transaction(request):
    return render(request, 'transactions/transaction.html')