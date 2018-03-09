from django.contrib import admin

# Register your models here.
from .models import clinicaltrial, file, block, adverseEvent

admin.site.register(clinicaltrial)
admin.site.register(file)
admin.site.register(block)
admin.site.register(adverseEvent)


