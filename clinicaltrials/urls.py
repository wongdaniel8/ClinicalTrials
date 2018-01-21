from django.conf.urls import url
from . import views 

app_name = 'clinicaltrial'

urlpatterns = [

#/clinicaltrials/
url(r'^$', views.index, name = 'index'),

#/clinicaltrials/register
url(r'^register$', views.UserFormView.as_view(), name = 'register'),

#/clinicaltrials/login
url(r'^login$', views.login, name = 'login'),

#/clinicaltrials/logout
url(r'^logout$', views.logout, name = 'logout'),

#/clinicaltrials/<trial ID>/ = 'detail' pattern
url(r'^(?P<clinicaltrial_id>[0-9]+)/$', views.detail, name = "detail")
]

