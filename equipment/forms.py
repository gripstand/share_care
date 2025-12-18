from django import forms
from .models import Equipment, EquipmentStatus
from share_care.select_choices import ALLOWED_TRANSITIONS
from datetime import datetime, timedelta, time

class DatePickerInput(forms.DateInput):
    input_type = 'date'

class EquipmentForm(forms.ModelForm):
    class Meta:
        widgets= {
                'eq_date':DatePickerInput(),
                'eq_owner': forms.RadioSelect,
        }
        model=Equipment
        fields='__all__'
        error_messages = {
            'eq_name': {
                'unique': "An equipment with this name already exists.",
                'required': "Equipment name is required.",
            },
        }

class EqStatusForm(forms.ModelForm):
    class Meta:
        model=EquipmentStatus
        widgets= {
             'status_date':DatePickerInput(),
             'equipment': forms.HiddenInput(),
        }
        fields=('status_notes','status_date','status','status_notes','client','equipment')

    def __init__(self, *args, **kwargs):
        # Pop the custom argument before calling super()
        last_status = kwargs.pop('last_status', None)
        last_client = kwargs.pop('last_client', None)
        super().__init__(*args, **kwargs)
                # Get the original choices from the model
        original_choices = self.fields['status'].choices
        
        print(f'The last status is {last_status} and last contact is {last_client}')
        if last_client:
            self.fields['client'].initial = last_client
        if last_status in ALLOWED_TRANSITIONS:
            allowed_values = ALLOWED_TRANSITIONS[last_status]
        else:
            # Default to no transitions if the last status is not handled
            allowed_values = []

        new_choices = []
        for value, display in original_choices:
            if value in allowed_values:
                new_choices.append((value, display))
                print(f"Adding {value} to choices") 
        self.fields['status'].choices = new_choices