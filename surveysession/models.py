from django.db import models
from zone.models import Zone
from observer.models import Observer
from survey.models import Survey

class Surveysession(models.Model):
    zone=models.ForeignKey(Zone,on_delete=models.CASCADE)
    observer=models.ForeignKey(Observer,on_delete=models.CASCADE)
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE)
    uploaded_at=models.DateField("uploaded_at",auto_now=True)
    url=models.CharField(max_length=100)
    number_session=models.CharField(max_length=20)
    start_date=models.DateField("start_date",auto_now=True)
    end_date=models.DateTimeField("end_date",auto_now=True)
    observational_distance=models.CharField(max_length=20)

    def __str__(self):
        return self.number_session
