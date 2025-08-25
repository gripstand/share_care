from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Client, AddContacts, Goal, GoalUpdate, Actions, Eval, Ticket
from django.forms import inlineformset_factory
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from datetime import date, timedelta
from share_care.widgets import ExpiryDateWidget
from share_care.fields import TimeSumField
#from .fields import TimeTrackWidget
#from bootstrap_datepicker_plus.widgets import DatePickerInput



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
             'dob':DatePickerInput(),
             'client_number':forms.HiddenInput(),
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
    goal_time_spent = TimeSumField(label="time spent")
    class Meta:
        model=Goal
        widgets= {
                'goal_date':DatePickerInput(),
                'goal_target_date':DatePickerInput(),
                'client': forms.HiddenInput(),
                'goal_status': forms.RadioSelect,
                #'goal_time_spent': TimeTrackWidget(),
                #'goal_time_spent': TimeSumField()
        }
        
        #fields = ['goal_date', 'goal_target_date', 'client', 'goal_status', 'goal_time_spent']
        fields='__all__'


class GoalUpdateForm(forms.ModelForm):
    goal_time_spent = TimeSumField(label="time spent")
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


class ActionForm(forms.ModelForm):
    class Meta:
        model=Actions
        widgets= {
                'action_date':DatePickerInput(),
                'action_follow_up_date':DatePickerInput(format="%m/%d/Y"),
                'client': forms.HiddenInput(),
                'action_outcome': forms.RadioSelect,
        }
        fields='__all__'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #today = date.today()
        # Add the onchange attribute to the select field
        self.fields['action_follow_up_period'].widget.attrs.update({
            'onchange': 'updateFollowUpDate()',
        })

 
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Check if a follow-up date was manually set by the user
        if self.cleaned_data.get('action_follow_up_date'):
            # Use the user-provided date and ignore the period
            instance.action_follow_up_date = self.cleaned_data.get('action_follow_up_date')
        
        # Otherwise, calculate the date based on the period
        else:
            follow_up_period = self.cleaned_data.get('action_follow_up_period')
            if follow_up_period:
                today = date.today()
                if follow_up_period == '1 Week':
                    instance.action_follow_up_date = today + timedelta(days=7)
                elif follow_up_period == '2 Weeks':
                    instance.action_follow_up_date = today + timedelta(days=14)
                elif follow_up_period == '3 Weeks':
                    instance.action_follow_up_date = today + timedelta(days=21)
                elif follow_up_period == '1 Month':
                    # This handles month addition more carefully
                    instance.action_follow_up_date = today.replace(month=today.month + 1)
                elif follow_up_period == '2 Months':
                    instance.action_follow_up_date = today.replace(month=today.month + 2)
                elif follow_up_period == '3 Months':
                    instance.action_follow_up_date = today.replace(month=today.month + 3)
                elif follow_up_period == '6 Months':
                    instance.action_follow_up_date = today.replace(month=today.month + 6)
                else:
                    instance.action_follow_up_date = None
            else:
                instance.action_follow_up_date = None

        if commit:
            instance.save()
        return instance


# ------------------- Tickets -------------------

class TicketForm(forms.ModelForm):
    class Meta:
        model=Ticket
        widgets= {
                
                'ticket_created_by': forms.HiddenInput(),
                'ticket_create_date':forms.HiddenInput(),
                'ticket_open': forms.HiddenInput(),
                'action': forms.HiddenInput(),
                'ticket_resolved_date':forms.HiddenInput(),
                
        }
        fields='__all__'


# ------------------- Evaluations -------------------

class EvalForm(forms.ModelForm):
    class Meta:
        model=Eval
        widgets= {
                'eval_date':DatePickerInput(),
                'client': forms.HiddenInput(),
                'eval_core_challenge': forms.RadioSelect
        }
        fields='__all__'