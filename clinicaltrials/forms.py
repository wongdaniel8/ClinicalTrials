from django.contrib.auth.models import User
from django import forms
from .models import file 


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

class DocumentForm(forms.ModelForm):
    
    class Meta:
        model = file 
        fields = ('clinicaltrial', 'owner', 'data' )
