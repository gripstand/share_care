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

