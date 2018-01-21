from django.db import models
from django.urls import reverse
from django.utils import timezone

# Create your models here.
class clinicaltrial(models.Model):
	author = models.CharField(max_length = 300)
	title = models.CharField(max_length = 300)
	# creation = models.CharField(max_length = 300)
	creationDate = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return "Title: " + self.title + " -- Author: " + self.author

class file(models.Model):
	clinicaltrial = models.ForeignKey(clinicaltrial, on_delete = models.CASCADE)
	filename = models.CharField(max_length = 100)
	file_type = models.CharField(max_length = 10)
	data = models.FileField()
	uploadDate = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.filename + self.file_type
