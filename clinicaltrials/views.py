from django.shortcuts import render, redirect
from django.http import Http404
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm
# from django.contrib.auth.forms import UserCreationForm

from .models import clinicaltrial, file  
# Create your views here.

def index(request):
	all_trials = clinicaltrial.objects.all()
	# template = loader.get_template('clinicaltrials/index.html')
	context = {'all_trials': all_trials }
	return render(request, 'clinicaltrials/index.html', context)

def detail(request, clinicaltrial_id):
	try:
		trial = clinicaltrial.objects.get(pk = clinicaltrial_id)
		# allFiles = file.objects.all(clinicaltrial = clinicaltrial_id) #why doesnt this work?
		allFiles = trial.file_set.all()
	except:
		raise Http404("trial does not exist")
	return render(request, 'clinicaltrials/detail.html', {'trial': trial, 'allFiles': allFiles})






class UserFormView(View):
	form_class = UserForm
	template_name = 'clinicaltrials/registration_form.html'
	
	#display blank form 
	def get(self, request):
		form = self.form_class(None)
		return render(request, self.template_name, {'form' : form})
		pass

	#process form data
	def post(self,request):
		form = self.form_class(request.POST)
		if form.is_valid():
			user = form.save(commit = False)
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			user.set_password(password)
			user.save()

			#return User objects if credentials are correct
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect('clinicaltrial:index')
		return render(request, self.template_name, {'form' :form})


def login(request):
	if request.method == 'GET':
		return render(request, 'clinicaltrials/login.html')
	
	if request.method == 'POST':
		


	
	
	

def logout(request):
	logout(request)
	all_trials = clinicaltrial.objects.all()
	context = {'all_trials': all_trials }
	return render(request, 'clinicaltrials/index.html', context)



