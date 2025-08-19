from django.db import models
from localflavor.us.models import USStateField
from django.utils import timezone
from django_currentuser.db.models import CurrentUserField
from phonenumber_field.modelfields import PhoneNumberField

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

class Client(MetaDataModel):
    last_name=models.CharField(max_length=150)
    first_name=models.CharField(max_length=150)
    dob=models.DateField(verbose_name="Date of Birth")
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
    PHONE_TYPE=(
        ('Home','Home'),
        ('Cell','Cell'),
        ('Office','Office'),
        ('Other', 'Other')
    )
    phone_main_type=models.CharField(max_length=7,choices=PHONE_TYPE,blank=False,default='Home')
    phone_secondary=PhoneNumberField(blank=True, null=True, region='US')
    phone_secondary_type=models.CharField(max_length=7,choices=PHONE_TYPE,blank=False,default='Home')
    cg_last_name=models.CharField(max_length=150,verbose_name="Care Giver Last Name", blank=True)
    cg_first_name=models.CharField(max_length=150,verbose_name="Care Giver First Name", blank=True)
    cg_email=models.EmailField(verbose_name="Care Giver Email", blank=True)
    cg_phone_main=models.CharField(max_length=20, verbose_name="Care Giver Phone", blank=True)
    cg_notes=models.TextField(verbose_name="Care Giver Notes", blank=True)

    def __str__(self):
        return self.last_name + ", " + self.first_name


# class Contact(models.Model):
#     client = models.ForeignKey(Client, on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20, blank=True)

class AddContacts(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='phone_numbers')
    add_contact_name=models.CharField(max_length=50)
    add_contact_phone_number=PhoneNumberField()
    PHONE_TYPE=(
        ('Home','Home'),
        ('Cell','Cell'),
        ('Office','Office'),
        ('Other', 'Other')
    )
    add_contact_phone_type=models.CharField(max_length=7,choices=PHONE_TYPE,blank=False,default='Home')

    def __str__(self):
        return str(self.phone_number)

    
class Goal(models.Model):
    goal_date=models.DateField()
    goal_name=models.CharField(max_length=30)
    GOALTYPES=(
        ('Measurable','Measurable'),
        ('Subjective','Subjective'),
        ('Mandated','Mandated'),
    )
    goal_type=models.CharField(max_length=25,choices=GOALTYPES,blank=False,default='Measurable')
    TRACKINGTYPES=(
        ('YN','Yes/No'),
        ('Progress','Progress'),
        ('None','None'),
    )
    goal_tack_type=models.CharField(max_length=25,choices=TRACKINGTYPES,blank=False,default='Progress')
    GOALSTATUSTYPE=(
        ('Open','Open'),
        ('Achieved','Achieved'),
        ('Archived', 'Archived'),
    )
    goal_time_spent=models.IntegerField()
    goal_status=models.CharField(max_length=25,choices=GOALSTATUSTYPE,blank=False,default='Open')
    goal_target_date=models.DateField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='goals')

    def __str__(self):
        return self.goal_name

class Progress(models.IntegerChoices):
    NOT_STARTED = 1, 'Not Started'
    NO_IMPROVEMENT = 2, 'No Improvement'
    SLIGTH_IMPROVEMENT = 3, 'Slight Improvement'
    CLOSE = 4, 'Close to Goal'
    COMPLETED = 5, 'Achieved'


class GoalUpdate(models.Model):
    g_update_date=models.DateField()
    GOALUPDATESTATUS=(
        ('Evaluated', 'Evaluated'),
        ('Achieved','Achieved'),
    )
    g_status_update=models.CharField(max_length=30,choices=GOALUPDATESTATUS, default='Evaluated')
    g_status_staff_time=models.IntegerField()
    g_status_progress_level = models.IntegerField(choices=Progress.choices,null=True,blank=True)
    goal=models.ForeignKey(Goal,on_delete=models.CASCADE, related_name='g_status_record')
    g_status_notes=models.TextField(null=True, blank=True)
