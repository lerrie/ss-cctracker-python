from django.shortcuts import render
from django.core.paginator import Paginator

from transactions.models import Transaction
from transactions.services import get_latest

def index(request):
    latest = get_latest()

    paginator = Paginator(latest, 25) #Shows 25 records per page
    page = request.GET.get('page')
    paged_latest = paginator.get_page(page)

    context = {
        'latest': paged_latest
    }

    return render(request, 'pages/index.html', context)