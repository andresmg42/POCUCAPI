from django.db import models
from option.models import Option
from visit.models import Visit
from question.models import Question

class Response(models.Model):
    option=models.ForeignKey(Option,on_delete=models.CASCADE,null=True)
    visita=models.ForeignKey(Visit,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE)
    numeric_value=models.IntegerField(null=True)
    text_value=models.CharField(max_length=30,null=True)

    def __str__(self):
        return self.numeric_value
