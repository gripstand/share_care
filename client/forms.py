from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Client, AddContacts, Goal, GoalUpdate
from django.forms import inlineformset_factory
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from datetime import datetime, timedelta, time



class DatePickerInput(forms.DateInput):
    input_type = 'date'

class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__ (*args, **kwargs)
       
        self.fields["email"].widget.attrs.update({
            'required':'',
            'placeholder':'Me@Somewhere.com',
         })
        self.fields["first_name"].widget.attrs.update({
            'required':'',
            'placeholder':'John',
         })
        self.fields["last_name"].widget.attrs.update({
            'required':'',
            'placeholder':'Doe',
         })

        self.fields["phone_main"].widget.attrs.update({
            'required':'',
            'placeholder':'(222) 555-1212',
         })
        self.fields["phone_secondary"].widget.attrs.update({
            'placeholder':'(222) 555-1212',
         })

    class Meta:
        model = Client
        widgets= {
             'dob':DatePickerInput()
        }
        fields='__all__'


class AddContactForm(forms.ModelForm):
    #phone_number = PhoneNumberField(region='US') # Example: sets a default region
    class Meta:
        model = AddContacts
        fields = '__all__'

PhoneNumberFormSet = inlineformset_factory(
    Client, 
    AddContacts,
    form=AddContactForm, 
    extra=1, 
    can_delete=False
)

PhoneNumberFormSetUpdate = inlineformset_factory(
    Client, 
    AddContacts, 
    form=AddContactForm, 
    extra=0, 
    can_delete=True
)


class GoalForm(forms.ModelForm):
    class Meta:
        model=Goal
        widgets= {
                'goal_date':DatePickerInput(),
                'goal_target_date':DatePickerInput(),
                'client': forms.HiddenInput(),
                'goal_status': forms.RadioSelect,
        }
        fields='__all__'

class GoalUpdateForm(forms.ModelForm):
    class Meta:
        model=GoalUpdate
        widgets= {
                'g_update_date':DatePickerInput(),
                'goal': forms.HiddenInput(),
        }
        fields='__all__'

    
    def __init__(self, *args, **kwargs):
        # Pop the custom argument before the super() call
        hide_progress_field = kwargs.pop('hide_progress_field', False)
        
        super().__init__(*args, **kwargs)

        # Check the condition and remove the field
        if hide_progress_field:
            self.fields.pop('g_status_progress_level')

# print(f"forms.py: PhoneNumberFormSetUpdate is of type {type(PhoneNumberFormSetUpdate)}")
