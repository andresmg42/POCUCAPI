from django.db import models
from subcategory.models import Subcategory
from questiontype.models import QuestionType
from surveyversion.models import SurveyVersion

class Question(models.Model):
    subacategory=models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    questiontype=models.ForeignKey(QuestionType,on_delete=models.CASCADE)
    surveyversion=models.ForeignKey(SurveyVersion,on_delete=models.CASCADE)
    code=models.CharField(max_length=3)
    description=models.CharField(max_length=30)

    def __str__(self):
        return self.code


