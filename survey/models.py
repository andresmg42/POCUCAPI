from django.db import models
from zone.models import Zone
from observer.models import Observer

class Survey(models.Model):
    zone= models.ForeignKey(Zone,on_delete=models.CASCADE)
    observer=models.ForeignKey(Observer,on_delete=models.CASCADE)
    url_uploaded_at=models.DateField("date_upload",auto_now=True)
    url=models.CharField(max_length=200)
    survey_number=models.IntegerField()
    start_date=models.DateField("start_date")
    end_date=models.DateField("end_date")
    observational_distance=models.FloatField()

    def __str__(self):
        return self.survey_number
