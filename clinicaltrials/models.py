from django.db import models

# Create your models here.
class clinicaltrial(models.Model):
	author = models.CharField(max_length = 300)
	title = models.CharField(max_length = 300)
	
	# startDate = models.TimeField(auto_now_add=True, blank=True)
	def __str__(self):
		return "Title: " + self.title + " -- Author: " + self.author

class file(models.Model):
	clinicaltrial = models.ForeignKey(clinicaltrial, on_delete = models.CASCADE)
	filename = models.CharField(max_length = 100)
	file_type = models.CharField(max_length = 10)
	
	# uploadDate = models.TimeField(auto_now_add=True, blank=True)
	def __str__(self):
		return self.filename + self.file_type
