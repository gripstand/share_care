from django.contrib import admin
from .models import Client, ReasonTopicsList, CoreChallengeList, CommunicationsList, ReferralEntities, FundingSources,GeneralDisabilityList # Register your models here.

admin.site.register(Client)
admin.site.register(ReasonTopicsList)
admin.site.register(CoreChallengeList)
admin.site.register(CommunicationsList)
admin.site.register(ReferralEntities)
admin.site.register(FundingSources)
admin.site.register(GeneralDisabilityList)