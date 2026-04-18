from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Instructor, Department

class CustomUserCreationForm(UserCreationForm):
    """Custom signup form for Instructor model with Department field."""
    Department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        help_text='Select your department (optional)',
        empty_label='-- Select Department --'
    )

    class Meta(UserCreationForm.Meta):
        model = Instructor
        fields = UserCreationForm.Meta.fields + ('email', 'FirstName', 'LastName', 'Department')

class EmailTimetableForm(forms.Form):
    """Form to send timetable via email."""
    email = forms.EmailField(label='Email Address')
    day = forms.ChoiceField(choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
    ])
    programme = forms.CharField(widget=forms.HiddenInput(), required=False)