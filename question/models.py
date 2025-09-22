from django.db import models
from subcategory.models import Subcategory
from survey.models import Survey
from option.models import Option

class Question(models.Model):
    subcategory=models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    options = models.ManyToManyField(
        Option,
        blank=True,
        related_name="questions"
    )
    code=models.CharField(max_length=3)
    question_type=models.CharField(max_length=20)
    description=models.TextField()
    parent_question=models.ForeignKey('self', on_delete=models.CASCADE,null=True,blank=True)
    survey=models.ManyToManyField(Survey,related_name='questions')

    def __str__(self):
        return self.code
    



