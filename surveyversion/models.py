from django.db import models
from topic.models import Topic

class SurveyVersion(models.Model):
    topic=models.ForeignKey(Topic,on_delete=models.CASCADE)
    name=models.CharField(max_length=20)

    def __str__(self):
        return self.name
    


    
