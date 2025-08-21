from django import template
from phonenumber_field.phonenumber import PhoneNumber

register = template.Library()

@register.filter
def format_phone(value):
    if not isinstance(value, PhoneNumber):
        return value

    # Use the national_number attribute to get only the digits
    national_number_str = str(value.national_number)

    # Check if the number has enough digits for a standard format
    if len(national_number_str) == 10:
        area_code = national_number_str[:3]
        first_three = national_number_str[3:6]
        last_four = national_number_str[6:]
        return f"({area_code}) {first_three}-{last_four}"

    # Return the value as is if it doesn't match the expected format
    return value.as_national