from django import template
from share_care.select_choices import EQStatusList, EquipmentTypes, EquipmentOwnerList

register = template.Library()

@register.simple_tag
def get_status_display(status_code):
    """Looks up the display name for a given status code."""
    # Convert choices to dictionary inside the tag
    # This logic assumes EQStatusList.choices is a list of tuples
    choices_map = dict(EQStatusList.choices) 
    return choices_map.get(status_code, 'Unknown Status')

@register.filter
def get(dictionary, key):
    """
    Allows dictionary key lookup in templates: {{ dictionary|get:key }}
    """
    # Use .get() method with a default value to prevent errors 
    # if a key is somehow missing or None.
    return dictionary.get(key, 'Unknown')