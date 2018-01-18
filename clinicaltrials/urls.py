from django.conf.urls import url
from . import views 

app_name = 'clinicaltrial'

urlpatterns = [
#/clinicaltrials/
url(r'^$', views.index, name = 'index'),

#/clinicaltrials/<trial ID>/ = detail 
url(r'^(?P<clinicaltrial_id>[0-9]+)/$', views.detail, name = "detail")
]