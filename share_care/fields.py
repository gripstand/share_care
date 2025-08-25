from django import forms
from .widgets import ExpiryDateWidget

# class TimeSumField(forms.MultiValueField):
#     widget = ExpiryDateWidget

#     def __init__(self, *args, **kwargs):
#         fields = (
#             # The first field for hours
#             forms.ChoiceField(
#                 choices=self.widget().get_hour_choices()
#             ),
#             # The second field for minutes
#             forms.ChoiceField(
#                 choices=self.widget().get_minute_choices()
#             ),
#         )
#         super().__init__(fields, *args, **kwargs)

#     def compress(self, data_list):
#         if data_list and all(data_list):
#             hours = int(data_list[0])
#             minutes = int(data_list[1])
#             # Sum the two values together as a single integer
#             return hours + minutes
#         return None


#         )
class TimeSumField(forms.MultiValueField):
    widget = ExpiryDateWidget

    def __init__(self, *args, **kwargs):
        fields = (
            # These fields are for validation, and must have the same choices as your widget
            forms.ChoiceField(choices=self.widget().get_hour_choices()),
            forms.ChoiceField(choices=self.widget().get_minute_choices()),
        )
        super().__init__(fields, *args, **kwargs)

    def value_from_datadict(self, data, files, name):
        # This method is crucial for getting the submitted data
        return [self.fields[0].widget.value_from_datadict(data, files, name + '_0'),
                self.fields[1].widget.value_from_datadict(data, files, name + '_1')]

    def compress(self, data_list):
        if data_list and all(data_list):
            # We must handle a potential IndexError
            try:
                hours = int(data_list[0])
                minutes = int(data_list[1])
                return hours + minutes
            except (ValueError, IndexError):
                # Return None if data is not valid
                return None
        return None