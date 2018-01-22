from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class clinicaltrial(models.Model):
	author = models.CharField(max_length = 300)
	title = models.CharField(max_length = 300)
	creationDate = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "Title: " + self.title + " -- Author: " + self.author

class file(models.Model):
	clinicaltrial = models.ForeignKey(clinicaltrial, on_delete = models.CASCADE, blank=True, null=True)
	owner = models.ForeignKey(User, on_delete = models.CASCADE, blank=True, null=True, unique = False)
	filename = models.CharField(max_length = 100)
	file_type = models.CharField(max_length = 100, blank=True, null = True) 
	data = models.FileField()
	uploadDate = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.filename 
