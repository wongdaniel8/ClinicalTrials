from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponse
from django.template import loader

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

