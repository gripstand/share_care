from django.shortcuts import render, redirect, get_object_or_404
from django import forms
from .models import Client, AddContacts, Goal, GoalUpdate, Actions, Eval, Ticket, TicketUpdate
from django.forms import inlineformset_factory
from django.forms import ModelForm
from phonenumber_field.formfields import PhoneNumberField
from datetime import date, timedelta
from share_care.widgets import ExpiryDateWidget
from share_care.fields import TimeSumField



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
        required_css_class = 'django-required'
        widgets= {
             'dob':DatePickerInput(),
             'client_number':forms.HiddenInput(),
        }
        fields='__all__'
        error_messages = {
            'first_name': {
                'required': "Client's first name is required."
            },
            'last_name': {
                'required': "Client's last name is required."
            },
            'email': {
                'required': "Client's email address is required."
            },
            'phone_main': {
                'required': "Client's primary phone number is required."
            },
            'zip': {
                'required': "Client's zip code is required."
            },
            'dob': {
                'required': "Client's date of birth is required."
            },
            'gen_disability': {
                'required': "Please select a general disability from the list."
            },
            'referred_by': {
                'required': "Please select a referral source from the list."
            },
            'street_address': {
                'required': "Client's street address is required."
            },
            'city': {
                'required': "Client's city is required."
            },
            'state': {
                'required': "Client's state is required."
            },

        }   


class AddContactForm(forms.ModelForm):
    #phone_number = PhoneNumberField(region='US') # Example: sets a default region
    class Meta:
        model = AddContacts
        fields = '__all__'
        error_messages = {
                'add_contact_name': {
                    'required': "Contact name is required."
                },

                'add_contact_phone': {
                    'required': "Contact phone number is required."
                },
            }    

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
    #goal_time_spent = TimeSumField(label="time spent")
    goal_name = forms.CharField(
        label="Goal Name",
        max_length=150,
        # Define a custom dictionary for all error types
        error_messages={
            'required': 'A name for the goal is required.'
        })
    class Meta:
        model=Goal
        widgets= {
                'goal_date':DatePickerInput(),
                'goal_target_date':DatePickerInput(),
                'client': forms.HiddenInput(),
                'goal_status': forms.RadioSelect,

        }
        
        fields='__all__'
        error_messages = {
            'goal_date': {
                'required': "A date for when this goal was set is required."
            },
            'goal_target_date': {
                'required': "A target completion date is required."
            },
            'goal_status': {
                'required': "Please set a status for the goal."
            }
        }



class GoalUpdateForm(forms.ModelForm):
    #goal_time_spent = TimeSumField(label="time spent")
    class Meta:
        model=GoalUpdate
        widgets= {
                'g_update_date':DatePickerInput(),
                'goal': forms.HiddenInput(),
        }
        fields='__all__'
        error_messages = {
            'goal_date': {
                'required': "A date for when this goal was set is required."
            },
            'goal_target_date': {
                'required': "A target completion date is required."
            },
            'goal_status': {
                'required': "Please set a status for the goal."
            },
            'g_status_staff_time': {
                'required': "Please enter the staff time spent on this update."
            }
        }

    
    def __init__(self, *args, **kwargs):
        # Pop the custom argument before the super() call
        hide_progress_field = kwargs.pop('hide_progress_field', False)
        
        super().__init__(*args, **kwargs)

        # Check the condition and remove the field
        if hide_progress_field:
            self.fields.pop('g_status_progress_level')



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
        error_messages = {
            'action_date': {
                'required': "A date for when this action item was created is required."
            },
            'action_notes': {
                'required': "Please enter notes for this action item."
            },
            'action_reason_code': {
                'required': "Please select a reason code from the list."
            }
        }



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
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Check if the form is being instantiated for a new object
        if not self.instance.pk: 
            pass
    class Meta:
        model=Ticket
        widgets= {
                
                'ticket_open': forms.HiddenInput(),
                'ticket_created_by': forms.HiddenInput(),
                'client': forms.HiddenInput(),
                'action': forms.HiddenInput(),
                'ticket_resolved_date':forms.HiddenInput()
        }
        fields='__all__'


class TicketUpdateForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ticket_update_by'].required = False
    class Meta:
        model = TicketUpdate
        widgets={
            'ticket_update_date':forms.HiddenInput(),
            'ticket': forms.HiddenInput(),
            'ticket_update_by': forms.HiddenInput(),
        }
        fields = '__all__'
        error_messages = {
            'ticket_update_notes': {
                'required': "Please enter notes for this ticket update."
            },
            'ticket_assign_to': {
                'required': "Please select a staff member to assign this ticket update to."
            }
        }


TicketUpdateFormSet = inlineformset_factory(
    Ticket, 
    TicketUpdate,
    form=TicketUpdateForm,
    fields=['ticket', 'ticket_assign_to', 'ticket_update_by'],
    extra=1, 
    can_delete=False
)



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
        error_messages = {
            'eval_user': {
                'required': "Please select the staff member completing this evaluation."
            },
            'eval_date': {
                'required': "A date for when this evaluation occured is required."
            },
            'eval_time': {
                'required': "Please enter the time spent on this evaluation."
            },
            'eval_core_challenge': {
                'required': "Please select a core challenge from the list."
            },
            'eval_communication': {
                'required': "Please select a communication capability from the list."
            },
            'eval_mobility': {
                'required': "Please select a mobility type from the list."
            },
            'eval_notes': {
                'required': "Please enter notes for this evaluation."
            }
        }