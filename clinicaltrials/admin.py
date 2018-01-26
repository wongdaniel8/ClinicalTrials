from django.contrib import admin

# Register your models here.
from .models import clinicaltrial, file, block 

admin.site.register(clinicaltrial)
admin.site.register(file)
admin.site.register(block)

