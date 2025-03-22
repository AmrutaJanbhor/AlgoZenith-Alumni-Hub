from django import forms

class AlumniSearchForm(forms.Form):
    query = forms.CharField(
        required=False, 
        label='Search Alumni',
        widget=forms.TextInput(attrs={'placeholder': 'Search by name...'})
    )