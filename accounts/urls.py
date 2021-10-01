from django.urls import path

from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('accttransactions', views.accttransactions, name='accttransactions'),
    path('accttransaction/<int:tran_id>', views.accttransaction, name='accttransaction'),
    path('accttransactiondelete/<int:tran_id>', views.accttransactiondelete, name='accttransactiondelete'),
]