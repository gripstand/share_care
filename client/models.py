from django.db import models
from users.models import CustomUser
from share_care.select_choices import PhoneTypes, GoalTypes, MobilityTypes, GoalStatusTypes, GoalTrackTypes, Progress, GoalUpdateStatusTypes
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


# ------------------ Models for Client Profile

class Client(MetaDataModel):
    client_number=models.IntegerField(unique=True, null=True, blank=True)
    last_name=models.CharField(max_length=150, verbose_name="Client Last Name")
    first_name=models.CharField(max_length=150, verbose_name="Client First Name")
    middle_name=models.CharField(max_length=150, blank=True, null=True, verbose_name="Client Middle Name")
    dob=models.DateField(verbose_name="Client Date of Birth")
    vet_status=models.BooleanField(default=False, verbose_name="Client is a veteran")
    active_status=models.BooleanField(default=True, verbose_name="Client is active")
    street_address=models.CharField(max_length=150)
    referred_by=models.ForeignKey(ReferralEntities, on_delete=models.CASCADE, blank=True, null=True, related_name='referred_by', verbose_name="Client referred by")
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
    eval_date=models.DateField()
    eval_user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='evals_by_user',verbose_name="Complete by")
    eval_time=models.IntegerField()
    eval_core_challenge=models.ForeignKey(CoreChallengeList, on_delete=models.CASCADE, related_name='eval_core_challenge', verbose_name="Core Challenge")
    eval_communication=models.ForeignKey(CommunicationsList, on_delete=models.CASCADE, related_name='eval_comm', verbose_name="Communication Capability")
    eval_mobility=models.CharField(max_length=50,choices=MobilityTypes.choices,blank=False,default='NORM')
    eval_notes=models.TextField()
    





#-------------------------------- Models for Goals

class Goal(models.Model):
    goal_date=models.DateField()
    goal_name=models.CharField(max_length=30)
    goal_type=models.CharField(max_length=25,choices=GoalTypes.choices,blank=False,default='MEASHURE')
    goal_tack_type=models.CharField(max_length=25,choices=GoalTrackTypes.choices,blank=False,default='YN')
    goal_time_spent=models.IntegerField()
    goal_status=models.CharField(max_length=25,choices=GoalStatusTypes.choices,blank=False,default='OPEN')
    goal_target_date=models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='goals')

    def __str__(self):
        return self.goal_name


class GoalUpdate(models.Model):
    g_update_date=models.DateField()
    g_status_update=models.CharField(max_length=30,choices=GoalUpdateStatusTypes.choices, default='EVAL')
    g_status_staff_time=models.IntegerField()
    g_status_progress_level = models.IntegerField(choices=Progress.choices,null=True,blank=True)
    goal=models.ForeignKey(Goal,on_delete=models.CASCADE, related_name='g_status_record')
    g_status_notes=models.TextField(null=True, blank=True)


#-------------------------------- Models for Actions


class Actions(models.Model):
    action_date=models.DateField()
    action_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use settings.AUTH_USER_MODEL for consistency
        on_delete=models.CASCADE,
        related_name='actions_by_user' # Give it a unique related_name
    )
    ACTIONTYPES=(
        ('Phone','Phone Call'),
        ('Virtual','Virtual Meetng'),
        ('In_Person','In Person'),
        ('Office_Visit', 'Office Visit'),
        ('Email','Email Exchange'),
        ('Text','Text Message'),
        ('TeamViewer','TeamViewer Consult'),
        ('HW/SW In', 'Hardware / Software Delieverd'),
        ('HW/SW Out', 'Hardware / Software Pick-Up'),
    )
    action_type=models.CharField(max_length=30,choices=ACTIONTYPES, default='Phone')
    INITBYTYPES=(
        ('Client','Client'),
        ('Caregiver','Caregiver'),
        ('SHARE','SHARE'),
        ('3rd_Party','3rd Party'),
    )
    action_init_by=models.CharField(max_length=30,choices=INITBYTYPES, default='Client')
    ACTIONOUTCOMES=(
        ('Successful','Successful'),
        ('Followup','Requires Follow-Up'),
    )
    action_outcome=models.CharField(max_length=30,choices=ACTIONOUTCOMES, default='Successful')
    action_reason_code=models.ForeignKey(ReasonTopicsList, on_delete=models.CASCADE, related_name='reason_for_action')
    action_notes=models.TextField(null=True, blank=True)
    client=models.ForeignKey(Client, on_delete=models.CASCADE, related_name='actions_for_client')

    def __str__(self):
        return self.action_date.strftime('%m-%d-%Y') + ' ' + self.action_type

