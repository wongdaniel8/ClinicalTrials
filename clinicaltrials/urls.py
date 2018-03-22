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
# url(r'^login$', views.UserLoginView.as_view(), name = 'login'),

#/clinicaltrials/logout
url(r'^logout$', views.userlogout, name = 'logout'),

#/clinicaltrials/user/
url(r'^user/$', views.userhome, name = 'userhome'),

#/clinicaltrials/<trial ID>/ = 'detail' pattern
url(r'^(?P<clinicaltrial_id>[0-9]+)/$', views.detail, name = "detail"),

#/clinicaltrials/upload = 'upload' pattern
# url(r'^upload(?P<inputFile>.*)$', views.model_form_upload, name = "upload"),
url(r'^upload$', views.model_form_upload, name = "upload"),


# url(r'^download/(?P<path>.*)$', serve, {'document root': settings.MEDIA_ROOT})

#/clinicaltrials/download/{path} = 'download' pattern
# url(r'^download/(?P<path>.*)$', views.download, name="download"),
url(r'^download/(?P<path>.*)/(?P<name>.*)$', views.download, name="download"),

# url(r'^decryptPDFdownload(?P<path>.*)$', views.decryptPDFdownload, name="decryptPDFdownload"),

#/clinicaltrials/CRF
url(r'^CRF$', views.CRF, name="CRF"),

#/clinicaltrials/downloadMultiple
url(r'^downloadMultiple$', views.downloadMultiple, name="downloadMultiple"),


# url(r'^decryptdownload/(?P<path>.*)$'
url(r'^decryptdownload(?P<path>.*)$', views.decryptdownload, name="decryptdownload")


]

if settings.DEBUG == True:
	urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)

	urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)



