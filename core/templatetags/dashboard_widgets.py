from django import template
from client.models import Client,Ticket  # Adjust the import if your app name is different

register = template.Library()

@register.inclusion_tag('widgets/active_client_stat.html')
def active_client_count():
    # Assuming you have a boolean field 'active' or similar
    count = Client.objects.filter(active_status=True).count()
    return {'count': count}

@register.inclusion_tag('widgets/user_ticket_count.html', takes_context=True)
def user_ticket_widget(context):
    request = context['request']
    if request.user.is_authenticated:
        count = Ticket.objects.filter(
            now_assigned_to=request.user,
            ticket_open=True
        ).count()
    else:
        count = 0
        
    return {
        'count': count,
        'user': request.user
    }