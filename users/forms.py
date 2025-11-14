from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.forms import ModelForm
from django.contrib.auth.models import Group
#from .widgets import DatePickerInput
#from bootstrap_datepicker_plus.widgets import DateTimePickerInput


class CustomUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__ (*args, **kwargs)
        # Define a hidden field
        self.fields["username"] = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,  # It's good practice to set hidden fields as not required
        
        )
        self.fields["groups"] = forms.ModelMultipleChoiceField(
            queryset=Group.objects.all(),
            required=False, # Groups are optional
            help_text="Select admin if user can administrate other users.",
            widget=forms.CheckboxSelectMultiple, # Use checkboxes for selection
            label="User Groups"
        )
        self.fields['access_to_system'] = forms.BooleanField(
            required=False,
            label='Access to System',
            help_text='Uncheck for individules that can be associated with data in the system, but will not be using this system.',
            initial=True,
        )
        self.fields['is_active'].required = False       
        self.fields["email"].widget.attrs.update({
            'class':'form-input',
            'placeholder':'Me@Somewhere.com',
         })
        self.fields["first_name"].widget.attrs.update({
            'class':'form-input',
            'required':'',
            'name':'first_name',
            'id':'first_name',
            'type':'text',
            'placeholder':'John',
         })

    class Meta:
        model = CustomUser
        fields = ['first_name','last_name','email','access_to_system','is_active','username','groups']
        error_messages = {
            'email': {
                'unique': "A user with that email already exists.",
                'required': "Email is required.",
            },
            'first_name': {
                'required': "First name is required.",
            },
            'last_name': {
                'required': "Last name is required.",
            },
        }
