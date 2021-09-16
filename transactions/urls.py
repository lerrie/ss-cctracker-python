from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='transactions'),
    path('<int:trans_id>', views.transaction, name='transaction'),
]