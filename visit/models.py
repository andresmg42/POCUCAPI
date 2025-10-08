from django.db import models
from surveysession.models import Surveysession
from django.dispatch import receiver
from django.db.models.signals import pre_delete


class Visit(models.Model):
    surveysession=models.ForeignKey(Surveysession,on_delete=models.CASCADE,related_name='visits')
    visit_number=models.IntegerField()
    visit_start_date_time=models.DateTimeField(null=True,blank=True)
    visit_end_date_time=models.DateTimeField(null=True,blank=True)
    state=models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['surveysession','visit_number'], 
                name='unique_visit_by_surveysession'
            )
        ]

    def __str__(self):
        return f'{self.surveysession.survey.name}-session-{self.surveysession.number_session}-visit-{self.visit_number}'

@receiver(pre_delete,sender=Visit)
def update_session_on_visit_delete(sender,instance,**kwargs):
    session=instance.surveysession
    if session:
        session.state=1
        session.end_date=None
        session.save(update_fields=['state','end_date'])


