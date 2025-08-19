from django import forms
from .models import Equipment, EquipmentStatus
from datetime import datetime, timedelta, time

class DatePickerInput(forms.DateInput):
    input_type = 'date'

class EquipmentForm(forms.ModelForm):
    class Meta:
        model=Equipment
        fields=['eq_name','eq_type', 'eq_value']

class EqStatusForm(forms.ModelForm):
       
    class Meta:
        model=EquipmentStatus
        widgets= {
             'status_date':DatePickerInput(),
             'equipment': forms.HiddenInput(),
        }
        fields='__all__'

    def __init__(self, *args, **kwargs):
        # Pop the custom argument before calling super()
        last_status = kwargs.pop('last_status', None)
        last_client = kwargs.pop('last_client', None)
        super().__init__(*args, **kwargs)
                # Get the original choices from the model
        original_choices = self.fields['status'].choices
        
        # Define allowed transitions
        allowed_transitions = {
            None: ['Inv'], # No previous status, so only 'In Inventory' is allowed
            'Inv': ['Client', 'Maint','Sunset', 'Unknown'],
            'Client': ['Return', 'Lost'],
            'Maint': ['Client', 'Inv', 'Sunset', 'Unknown', 'Lost'],
            'Lost': ['Sunset', 'Inv', 'Unknown'],
            'RTO': ['Sunset'],
            'Sunset': ['Inv'],
            'Unknown': ['Inv','Client'],
            'Return': ['Inv','Client', 'Maint','Sunset', 'Unknown'],
        }
        print(f'The last status is {last_status} and last contact is {last_client}')
        if last_client:
            self.fields['client'].initial = last_client
        if last_status in allowed_transitions:
            allowed_values = allowed_transitions[last_status]
        else:
            # Default to no transitions if the last status is not handled
            allowed_values = []

        new_choices = []
        for value, display in original_choices:
            if value in allowed_values:
                new_choices.append((value, display))
        
        self.fields['status'].choices = new_choices