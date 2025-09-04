from django.db import models
from survey.models import Survey

class Visita(models.Model):
    survey=models.ForeignKey(Survey,on_delete=models.CASCADE)
    visit_number=models.IntegerField()
    visit_date=models.DateField(auto_now=True)
    start_time=models.TimeField()
    end_time=models.TimeField()

    def __str__(self):
        return self.visit_number




