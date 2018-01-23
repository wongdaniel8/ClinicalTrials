from django.conf.urls import url
from . import views 
from django.conf import settings
from django.conf.urls.static import static


app_name = 'clinicaltrial'

urlpatterns = [

#/clinicaltrials/
url(r'^$', views.index, name = 'index'),

#/clinicaltrials/register
url(r'^register$', views.UserFormView.as_view(), name = 'register'),

#/clinicaltrials/login
url(r'^login$', views.userlogin, name = 'login'),

#/clinicaltrials/logout
url(r'^logout$', views.userlogout, name = 'logout'),

#/clinicaltrials/user/
url(r'^user/$', views.userhome, name = 'userhome'),

#/clinicaltrials/<trial ID>/ = 'detail' pattern
url(r'^(?P<clinicaltrial_id>[0-9]+)/$', views.detail, name = "detail"),

#/clinicaltrials/upload = 'upload' pattern
url(r'^upload$', views.model_form_upload, name = "upload"),

# url(r'^download/(?P<path>.*)$', serve, {'document root': settings.MEDIA_ROOT})
url(r'^download/(?P<path>.*)$', views.download, name="download")


]

if settings.DEBUG == True:
	urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)

	urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)



