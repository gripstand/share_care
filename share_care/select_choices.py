from django.db import models

############################ 
# This file contains classes of lists which are used throught the system to populate drop down select boxes
# While adding to these lists should have no impact on the system, deleting choices already saved may
# cause issues in data that has already been saved.
############################ 

class PhoneTypes(models.TextChoices):
    HOME='Home','Home'
    CELL='Cell', 'Cell'
    OFFICE='Office', 'Office'
    OTHER='Other','Other'

class GoalTypes(models.TextChoices):
    MEASHURE='Measurable','Measurable'
    SUBJ='Subjective','Subjective'
    MAND='Mandated','Mandated'

class MobilityTypes(models.TextChoices):
    NORM='Normal','Normal'
    SOMEWHAT='Somewhat Limited','Somewhat Limited'
    SEVERALLY='Severally Limited','Severally Limited'
    WHEELCHAIR='Wheelchair','Wheelchair'
    BEDRIDDEN='Bedridden','Bedridden'

class GoalTrackTypes(models.TextChoices):
   YN='Yes/No','Yes/No'
   PROG='Progress','Progress'
   NONE='None','None'

class GoalStatusTypes(models.TextChoices):
    OPEN='Open','Open'
    ACH='Achieved','Achieved'
    ARCHIVE='Archived', 'Archived'

class GoalUpdateStatusTypes(models.TextChoices):
    EVAL='Evaluated','Evaluated'
    ACH='Achieved','Achieved'


class Progress(models.IntegerChoices):
    NOT_STARTED = 1, 'Not Started'
    NO_IMPROVEMENT = 2, 'No Improvement'
    SLIGTH_IMPROVEMENT = 3, 'Slight Improvement'
    CLOSE = 4, 'Close to Goal'
    COMPLETED = 5, 'Achieved'

class EQStatusList(models.TextChoices):
    # Correct Syntax: (database_value, human_readable_name)
    INV = 'INV', 'In Inventory'
    CLIENT = 'CLIENT', 'With Client'
    RETURN = 'RETURN', 'Returned from Client'
    MAINT = 'MAINT', 'Maintenance'
    SUNSET = 'SUNSET', 'Sunset'
    LOST = 'LOST', 'Lost'
    RTO = 'RTO', 'Returned to owner'
    UNKNOWN = 'UNKNOWN', 'Unknown'

# The allowed transaction dictionary will need to get altered if you add or remove any of the above choices
# This is used in the EquipmentStatusForm to determine what status choices are available based on the
# last status of the equipment.
# The keys are the last status and the values are the allowed next statuses.
# If the last status is None, it means the equipment has never had a status before,
# so the only allowed next status is 'INV' (In Inventory).
# If the last status is not in the dictionary, it means no transitions are allowed.

ALLOWED_TRANSITIONS = {
    None: ['INV'], # No previous status, so only 'In Inventory' is allowed
    'INV': ['CLIENT', 'MAINT', 'SUNSET', 'UNKNOWN'],
    'CLIENT': ['RETURN', 'LOST'],
    'MAINT': ['CLIENT', 'INV', 'SUNSET', 'UNKNOWN', 'LOST'],
    'LOST': ['SUNSET', 'INV', 'UNKNOWN'],
    'RTO': ['SUNSET'],
    'SUNSET': ['INV'],
    'UNKNOWN': ['INV', 'CLIENT'],
    'RETURN': ['INV', 'CLIENT', 'MAINT', 'SUNSET', 'UNKNOWN'],
}


class EquipmentTypes(models.TextChoices):
    SYSTEM='System','System'
    LAPTOP='Laptop','Laptop'
    DESKTOP='Desktop','Desktop'
    IPAD='iPad','iPad'
    CELL='Cell Phone','Cell Phone'
    EYEGAZE='Eye Gaze','Eye Gaze'
    SDRAGON='Software-Dragon','Software-Dragon'
    STOBII='Software-Tobii','Software-Tobii'
    SVISION='Software-Vision','Software-Vision'
    SOTHER='Software-Other','Software-Other'
    PERIPHERAL='Peripheral','Peripheral'
    INTERFACE='Interface','Interface'
    SOFTWARE='Software','Software'
    OTHER='Other','Other'

class EquipmentOwnerList(models.TextChoices):
    CLIENT='Client','Client'
    FOUNDATION='Foundation','Foundation'
    THIRD_PARTY='Third Party','Third Party'
    
class ActionTypes(models.TextChoices):
    PHONE='Phone Call','Phone Call',
    VIRTUAL='Virtual Meeting','Virtual Meeting',
    IN_PERSON='In Person','In Person',
    OFFICE_VISIT='Office Visit','Office Visit',
    EMAIL='Email Exchange','Email Exchange',
    TRAIN= 'Training','Training Request',
    EQ_ISSUE='Equipment Issue','Equipment Issue',
    TEXT='Text Message','Text Message',
    TEAMVIEWER='TeamViewer Consult','TeamViewer Consult',
    HW_SW_IN='Hardware / Software Delivered','Hardware / Software Delivered',
    HW_SW_OUT='Hardware / Software Pick-Up','Hardware / Software Pick-Up'


class ActionInitByTypes(models.TextChoices):
    CLIENT='Client','Client'
    CAREGIVER='Caregiver','Caregiver'
    SHARE='SHARE','SHARE'
    THIRD_PARTY='3rd Party','3rd Party'

class ActionOutcomeList(models.TextChoices):
    SUCCESSFUL='Successful','Successful'
    FOLLOWUP='Requires Follow-Up','Requires Follow-Up'


class ActionFollowUpPeriod(models.TextChoices):
    ONE_WEEK='1 Week','1 Week'
    TWO_WEEKS='2 Weeks','2 Weeks'
    THREE_WEEKS='3 Weeks','3 Weeks'
    ONE_MONTH='1 Month','1 Month'
    TWO_MONTHS='2 Months','2 Months'
    THREE_MONTHS='3 Months','3 Months'
    SIX_MONTHS='6 Months','6 Months'
    OTHER='Other','Other'

class TicketStatusTypes(models.TextChoices):
    ACTIVE='Active','Active'
    RESOLVED='Resolved','Resolved'
    CANCELED='Canceled','Canceled'
    PENDING='Pending','Pending'
    ON_HOLD='On Hold','On Hold'