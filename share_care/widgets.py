from django import forms
from django.forms.widgets import Select, TextInput, MultiWidget

class DatePickerInput(forms.DateInput):
    input_type = 'date'

# class TimeTrackWidget(forms.MultiWidget):
#     """
#     A widget that renders two select fields for hours and minutes.
#     """
    # def __init__(self, attrs=None):
    #     use_required_attribute = True # Add this line
    #     # if attrs is None:
    #     #     attrs = {}
            
    #     widgets = [
    #         Select(attrs={'class':'custom-time-select'}, choices=self.get_hour_choices()),
    #         Select(attrs={'class':'custom-time-select'}, choices=self.get_minute_choices()),
    #     ]

    #     super().__init__(widgets, attrs)
        
    # def decompress(self, value):
    #     if value:
    #         # Assuming value is a string like "1 Hour+30 Min"
    #         parts = value.split('+')
    #         return [parts[0], parts[1]]
    #     return [None, None]

    # def get_hour_choices(self):
    #     return [
    #         (4,'1 Hour'),
    #         (8, '2 Hours'),
    #         (12, '3 Hours')
    #     ]
        
    # def get_minute_choices(self):
    #     return [
    #         (0, '00 Min'),
    #         (15, '15 Min'),
    #         (30, '30 Min'),
    #         (45, '45 Min')
    #     ]


class ExpiryDateWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        _widgets = (
            #forms.TextInput(attrs={'placeholder': 'MM', 'maxlength': '2', 'size': '2'}),
            #forms.TextInput(attrs={'placeholder': 'YYYY', 'maxlength': '4', 'size': '4'}),
            forms.Select(attrs={'placeholder': 'MM'}, choices=self.get_hour_choices()),
            forms.Select(attrs={'placeholder': 'YYYY'}, choices=self.get_minute_choices()),
        
        )
        super().__init__(_widgets, attrs)

    def get_hour_choices(self):
        return [
            (4,'1 Hour'),
            (8, '2 Hours'),
            (12, '3 Hours')
        ]
        
    def get_minute_choices(self):
        return [
            (0, '00 Min'),
            (1, '15 Min'),
            (2, '30 Min'),
            (3, '45 Min')
        ] 
    
    def decompress(self, value):
        if value:
            # Assuming value is a string like "MM/YYYY"
            return [value.hours, value.minutes]
        return [None, None]

    def format_output(self, rendered_widgets):
        # Customize how the sub-widgets are rendered together
        return f'<div class="d-flex">{rendered_widgets[0]}{rendered_widgets[1]}</div>'

class TimeTrackWidget(forms.MultiWidget):
    pass
