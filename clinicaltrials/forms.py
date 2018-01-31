from django.contrib.auth.models import User
from django import forms
from .models import file 


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password']

class LoginForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'password']

class DocumentForm(forms.ModelForm):
    # password = forms.CharField(widget=forms.PasswordInput)
    # use_required_attribute = False

    # def clean(self):
    #     data = self.cleaned_data
    #     print(data)
    #     print(data.get('encrypted'), data.get('password') == '')
    #     if data.get('encrypted') == True and data.get('password') == '':
    #         print("rawr")
    #         raise forms.ValidationError('Provide a password if encryption selected') #not raising for some reason
    #     return self.cleaned_data
   
    
    class Meta:
        model = file 
        fields = ('clinicaltrial', 'owner', 'encrypted', 'password', 'data' )
