#simple forms
from django import forms

class Inputform(forms.Form):
    s_usn = forms.CharField(label = 'Enter USN: ', max_length = 10)

class BookSearchForm(forms.Form):
    query = forms.CharField(label='Search for books', max_length=100, required=False)
    author = forms.CharField(label='Author', max_length=100, required=False)
    category = forms.CharField(label='Category', max_length=100, required=False)
    isbn = forms.CharField(label='ISBN', max_length=13, required=False)
