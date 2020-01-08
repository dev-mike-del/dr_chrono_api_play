from django.contrib import admin

from .models import Patient


class PatientAdmin(admin.ModelAdmin):
	list_display = ('id', 'first_name', 'last_name',)


admin.site.register(Patient, PatientAdmin)
