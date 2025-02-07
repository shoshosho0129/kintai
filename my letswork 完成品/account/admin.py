from django.contrib import admin
from .models import Account_e
from .models import Account_a

admin.site.register(Account_e)
@admin.register(Account_a)
class Account_aAdmin(admin.ModelAdmin):
    list_display = ['a_no', 'a_first', 'a_last', 'is_active', 'is_staff']