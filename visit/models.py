from django.db import models
from surveysession.models import Surveysession

class Visit(models.Model):
    surveysession=models.ForeignKey(Surveysession,on_delete=models.CASCADE)
    visit_number=models.IntegerField()
    visit_date=models.DateField(auto_now=True)
    start_time=models.TimeField()
    end_time=models.TimeField()
    complete=models.BooleanField(default=False)

    def __str__(self):
        return str(self.visit_number)




