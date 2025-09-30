from django.db import models
from surveysession.models import Surveysession

class Visit(models.Model):
    surveysession=models.ForeignKey(Surveysession,on_delete=models.CASCADE)
    visit_number=models.IntegerField()
    visit_date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    complete=models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['surveysession','visit_number'], 
                name='unique_visit_by_surveysession'
            )
        ]

    def __str__(self):
        return f'{self.surveysession.survey.name}-session-{self.surveysession.number_session}-visit-{self.visit_number}'




