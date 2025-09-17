from django.db import models
from subcategory.models import Subcategory
from survey.models import Survey

class Question(models.Model):
    subacategory=models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    code=models.CharField(max_length=3)
    question_type=models.CharField(max_length=20)
    description=models.TextField()
    survey=models.ManyToManyField(Survey,related_name='questions')

    def __str__(self):
        return self.code
    

# class Question_Survey(models.Model):
#     question=models.ForeignKey(Question,on_delete=models.CASCADE)
#     survey=models.ForeignKey(Survey,on_delete=models.CASCADE)
#     order_question=models.IntegerField()

#     class Meta:
#         unique_together=("question","survey")
    
#     def __str__(self):
#         return f"{self.question} belong to {self.survey}" 

