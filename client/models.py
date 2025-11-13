from django.db import models
from users.models import CustomUser
from share_care.select_choices import PhoneTypes, GoalTypes, MobilityTypes, GoalStatusTypes, GoalTrackTypes, Progress, GoalUpdateStatusTypes, ActionInitByTypes, ActionOutcomeList, ActionTypes, ActionFollowUpPeriod, TicketStatusTypes
from localflavor.us.models import USStateField
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

# Create your models here.

class MetaDataModel(models.Model):
    """
    An abstract base class model that provides self-updating
    `created` and `modified` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # This field now has a unique related_name
    created_by = CurrentUserField(related_name='created_record')
    updated_by = CurrentUserField(on_update=True, blank=True, null=True, related_name='updated_record')
    class Meta:
        abstract = True

# ------------------ Models for lists where CRUD is only in the ADMIN

class ReasonTopicsList(models.Model):
    reason_topics=models.CharField(max_length=250)
    reason_topic_code=models.CharField(max_length=5)

    def __str__(self):
        return self.reason_topics
    
class CoreChallengeList(models.Model):
    core_challenge=models.CharField(max_length=150, verbose_name="Core Challenge")

    def __str__(self):
        return self.core_challenge

class CommunicationsList(models.Model):
    comm_type=models.CharField(max_length=150, verbose_name="Communication Types")

    def __str__(self):
        return self.comm_type
    
class ReferralEntities(models.Model):
    ref_name=models.CharField(max_length=150, verbose_name="Entity Name")
    ref_phone=PhoneNumberField(null=True, blank=True, verbose_name="Phone Number")
    ref_contact_name=models.CharField(max_length=150, null=True, blank=True, verbose_name="Contact Name")
    ref_active_status=models.BooleanField(default=True, verbose_name="Entity is active")

    def __str__(self):
        return self.ref_name

class FundingSources(models.Model):
    fund_name=models.CharField(max_length=150, verbose_name="Fund Name")
    fund_active_status=models.BooleanField(default=True, verbose_name="Fund is active")

    def __str__(self):
        return self.fund_name

class GeneralDisabilityList(models.Model):
    disability_name=models.CharField(max_length=150, verbose_name="Disability Name")
    
    def __str__(self):
        return self.disability_name

# ------------------ Models for Client Profile

class Client(MetaDataModel):
    client_number=models.IntegerField(unique=True, null=True, blank=True)
    last_name=models.CharField(max_length=150, verbose_name="Client Last Name")
    first_name=models.CharField(max_length=150, verbose_name="Client First Name")
    middle_name=models.CharField(max_length=150, blank=True, null=True, verbose_name="Client Middle Name")
    dob=models.DateField(verbose_name="Client Date of Birth")
    vet_status=models.BooleanField(default=False, verbose_name="Client is a veteran")
    active_status=models.BooleanField(default=True, verbose_name="Client is active")
    referred_by=models.ForeignKey(ReferralEntities, on_delete=models.CASCADE, related_name='referred_by', verbose_name="Client referred by")
    gen_disability=models.ForeignKey(GeneralDisabilityList, on_delete=models.CASCADE, related_name='gen_disability', verbose_name="General Disability")
    disability_notes=models.TextField(blank=True, null=True, verbose_name="Disability Notes")
    street_address=models.CharField(max_length=150)
    street_address_2=models.CharField(max_length=150, blank=True)
    city=models.CharField(max_length=150)
    state=USStateField()
    zip=models.CharField(max_length=15)
    mailing_same=models.BooleanField(default=False, verbose_name="Mailing same as home")
    mail_street_address=models.CharField(max_length=150, blank=True)
    mail_street_address_2=models.CharField(max_length=150, blank=True)
    mail_city=models.CharField(max_length=150, blank=True)
    mail_state=USStateField(blank=True)
    mail_zip=models.CharField(max_length=15, blank=True)
    email=models.EmailField()
    phone_main=PhoneNumberField()
    phone_main_type=models.CharField(max_length=7,choices=PhoneTypes.choices,blank=False,default='HOME')
    phone_secondary=PhoneNumberField(blank=True, null=True, region='US')
    phone_secondary_type=models.CharField(max_length=7,choices=PhoneTypes.choices,blank=False,default='CELL')
    cg_last_name=models.CharField(max_length=150,verbose_name="Care Giver Last Name", blank=True)
    cg_first_name=models.CharField(max_length=150,verbose_name="Care Giver First Name", blank=True)
    cg_email=models.EmailField(verbose_name="Care Giver Email", blank=True)
    cg_phone_main=models.CharField(max_length=20, verbose_name="Care Giver Phone", blank=True)
    cg_notes=models.TextField(verbose_name="Care Giver Notes", blank=True)

    def save(self, *args, **kwargs):
        # Only set a number if the field is empty (for a new record)
        if not self.client_number:
            # Find the last record and get its client_number
            last_client = Client.objects.order_by('-client_number').first()
            if last_client:
                # If a record exists, increment its number by 1
                self.client_number = last_client.client_number + 1
            else:
                # If this is the very first record, start at 1
                self.client_number = 1000
        
        # Call the parent save method to actually save the object to the database
        super().save(*args, **kwargs)


    def __str__(self):
        return self.last_name + ", " + self.first_name



class AddContacts(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='phone_numbers')
    add_contact_name=models.CharField(max_length=50)
    add_contact_phone_number=PhoneNumberField()
    add_contact_phone_type=models.CharField(max_length=7,choices=PhoneTypes.choices,blank=False,default='HOME')

    def __str__(self):
        return str(self.phone_number)

#------------------------------- Models for Evaluations

class Eval(models.Model):
    eval_date=models.DateField(verbose_name="Date of Evaluation", default=timezone.now)
    eval_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='evals_by_user',verbose_name="Complete By")
    eval_time=models.IntegerField(verbose_name="Time Spent (in minutes)")
    eval_core_challenge=models.ForeignKey(CoreChallengeList, on_delete=models.CASCADE, related_name='eval_core_challenge', verbose_name="Core Challenge")
    eval_communication=models.ForeignKey(CommunicationsList, on_delete=models.CASCADE, related_name='eval_comm', verbose_name="Communication Capability")
    eval_mobility=models.CharField(max_length=50,choices=MobilityTypes.choices,blank=False,default='NORM',verbose_name="Client Mobility")
    eval_notes=models.TextField(verbose_name="Evaluation Notes")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='evals_for_client')
    
    def __str__(self):
        return 'Evaluation on ' + self.eval_date.strftime('%m-%d-%Y') + ' by ' + self.eval_user.last_name + ', ' + self.eval_user.first_name




#-------------------------------- Models for Goals

class Goal(models.Model):
    goal_date=models.DateField()
    goal_name=models.CharField(max_length=30)
    goal_type=models.CharField(max_length=25,choices=GoalTypes.choices,blank=False,default='MEASHURE')
    goal_tack_type=models.CharField(max_length=25,choices=GoalTrackTypes.choices,blank=False,default='YN')
    goal_time_spent=models.IntegerField(verbose_name="Staff Time Spent (in minutes)")
    goal_status=models.CharField(max_length=25,choices=GoalStatusTypes.choices,blank=False,default='OPEN')
    goal_target_date=models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='goals')

    def __str__(self):
        return self.goal_name


class GoalUpdate(models.Model):
    g_update_date=models.DateField(verbose_name="Date of Update", default=timezone.now)
    g_status_update=models.CharField(max_length=30,choices=GoalUpdateStatusTypes.choices, default='EVAL',verbose_name="Goal Status Update")
    g_status_staff_time=models.IntegerField(verbose_name="Staff Time Spent (in minutes)")
    g_status_progress_level = models.IntegerField(choices=Progress.choices,null=True,blank=True)
    goal=models.ForeignKey(Goal,on_delete=models.CASCADE, related_name='g_status_record')
    g_status_notes=models.TextField(null=True, blank=True,verbose_name="Notes about this update")


#-------------------------------- Models for Actions


class Actions(models.Model):
    action_date=models.DateField(default=timezone.now)
    action_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL for consistency
        on_delete=models.CASCADE,
        related_name='actions_by_user' # Give it a unique related_name
    )
    action_type=models.CharField(max_length=30,choices=ActionTypes.choices, default='Phone Call')
    action_init_by=models.CharField(max_length=30,choices=ActionInitByTypes.choices, default='Client')
    action_outcome=models.CharField(max_length=30,choices=ActionOutcomeList.choices, default='Successful')
    action_follow_up_period=models.CharField(max_length=30,choices=ActionFollowUpPeriod.choices, blank=True, null=True)
    action_follow_up_date=models.DateField(null=True, blank=True, verbose_name="Follow Up Date")
    action_reason_code=models.ForeignKey(ReasonTopicsList, on_delete=models.CASCADE, related_name='reason_for_action')
    action_notes=models.TextField(null=True, blank=True)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, related_name='actions_for_client')
    action_ticket_created=models.BooleanField(default=False)

    def __str__(self):
        return self.action_date.strftime('%m-%d-%Y') + ' ' + self.action_type

class Ticket(models.Model):
    ticket_slug=models.CharField(max_length=30, verbose_name="Ticket Short Name")
    ticket_create_date=models.DateField(default=timezone.now)
    ticket_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL for consistency
        on_delete=models.CASCADE,
        related_name='tickets_created_by_user',
        verbose_name="Ticket created by"
    )
    ticket_issue=models.TextField(verbose_name="Issue Description")
    ticket_status=models.CharField(choices=TicketStatusTypes.choices, max_length=30, default='ACTIVE', verbose_name="Ticket Status")
    ticket_resolved_date=models.DateField(null=True, blank=True, verbose_name="Resolved Date")
    ticket_open=models.BooleanField(default=True)
    action=models.ForeignKey(Actions, on_delete=models.CASCADE, related_name='ticket_for_action')

    def __str__(self):
        return self.ticket_slug
    
class TicketUpdate(models.Model):
    ticket=models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='updates_for_ticket')
    ticket_update_date=models.DateField(default=timezone.now)
    ticket_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL for consistency
        on_delete=models.CASCADE,
        related_name='ticket_updates_by_user', # Give it a unique related_name
        verbose_name="Update by",
    )
    ticket_assign_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_assigned_to_user',
        verbose_name="Assign to"
    )
    ticket_update_notes=models.TextField(verbose_name="Ticket Update Notes")

    def __str__(self):
        return f"Update on {self.ticket_update_date} by {self.ticket_update_by}"
    
 