from django import forms
from django.contrib import admin

from .models import Transaction
from .services import get_exchanges, get_coins

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'
        widgets = {
            'exchange': forms.Select(),
            'coin': forms.Select(),
        }
        
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionForm
    
    list_display = ('coin', 'exchange', 'purchasedDate', 'Price_USD', 'qty', 'Fees_USD')
    list_filter = ('purchasedDate',)
    fields = ('coin', 'exchange', 'purchasedDate', 'priceAtBought', 'qty', 'fees', 'notes')
    search_fields = ('coin', 'exchange')
    ordering = ('-purchasedDate',)
    list_per_page = 25
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "exchange":
            kwargs['widget'].choices = get_exchanges()
        if db_field.name == "coin":
            kwargs['widget'].choices = get_coins()
        return super(TransactionAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def Price_USD(self, db_field):
        return '$ {:,}'.format(round(db_field.priceAtBought,2))

    def Fees_USD(self, db_field):
        return '$ {:,}'.format(round(db_field.fees,2))
    
admin.site.register(Transaction, TransactionAdmin)