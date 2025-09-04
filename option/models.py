from django.db import models
from question.models import Question

class Option(models.Model):
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    description=models.CharField(max_length=30)

    def __str__(self):
        return self.description
    

