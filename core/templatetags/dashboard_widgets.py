from django import template
from client.models import Client  # Adjust the import if your app name is different

register = template.Library()

@register.inclusion_tag('widgets/active_client_stat.html')
def active_client_count():
    # Assuming you have a boolean field 'active' or similar
    count = Client.objects.filter(active_status=True).count()
    return {'count': count}