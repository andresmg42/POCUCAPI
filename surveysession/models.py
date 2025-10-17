from django.db import models
from zone.models import Zone
from observer.models import Observer
from survey.models import Survey

class Surveysession(models.Model):
    zone=models.ForeignKey(Zone,on_delete=models.CASCADE)
    observer=models.ForeignKey(Observer,on_delete=models.CASCADE,related_name='surveysessions')
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE,related_name='sessions')
    uploaded_at=models.DateField("uploaded_at",auto_now_add=True)
    url=models.CharField(max_length=100)
    number_session=models.CharField(max_length=20)
    start_date=models.DateTimeField(null=True,blank=True)
    end_date=models.DateTimeField(null=True,blank=True)
    observational_distance=models.CharField(max_length=20)
    visit_number=models.IntegerField(null=False,default=6)
    state=models.IntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['survey','number_session','observer'], 
                name='unique_number_session_by_survey_by_observer'
            )
        ]

    def __str__(self):
        return f'{self.survey.name}-session-{self.number_session}'
