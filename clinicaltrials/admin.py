from django.contrib import admin

# Register your models here.
from .models import clinicaltrial, file 

admin.site.register(clinicaltrial)
admin.site.register(file)

