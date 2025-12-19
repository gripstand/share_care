from client.models import Ticket

for ticket in Ticket.objects.all():
    latest = ticket.updates_for_ticket.order_by('-ticket_update_date', '-id').first()
    if latest:
        ticket.now_assigned_to = latest.ticket_assign_to
        ticket.save(update_fields=['now_assigned_to'])
        print(f"Synced Ticket: {ticket.ticket_slug}")