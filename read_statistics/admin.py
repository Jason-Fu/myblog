from django.contrib import admin
from .models import ReadNumber,ReadNumberByDay

@admin.register(ReadNumber)
class ReadNumberAdmin(admin.ModelAdmin):
    list_display = ('read_number','content_object')

@admin.register(ReadNumberByDay)
class ReadNumberByDayAdmin(admin.ModelAdmin):
    list_display = ('date','read_number', 'content_object')