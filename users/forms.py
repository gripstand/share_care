from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from django.forms import ModelForm
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
        self.fields["email"].widget.attrs.update({
            'class':'form-input',
            'required':'',
            'name':'email',
            'id':'email',
            'type':'email',
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
        fields = ['first_name','last_name','email','access_to_system','is_active','username','admin_account']
