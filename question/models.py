from django.db import models
from subcategory.models import Subcategory
from survey.models import Survey
from option.models import Option



class Question(models.Model):

    class InputType(models.TextChoices):
        NUMERIC='NUM','Numerico'
        TEXT='STR','Textual'

    subcategory=models.ForeignKey(Subcategory,on_delete=models.CASCADE)
    options = models.ManyToManyField(
        Option,
        blank=True,
        related_name="questions"
    )
    code=models.CharField(max_length=20)
    question_type=models.CharField(max_length=20)
    description=models.TextField()
    parent_question=models.ForeignKey('self', on_delete=models.CASCADE,null=True,blank=True,related_name='child_questions')
    survey=models.ManyToManyField(Survey,related_name='questions')
    is_required=models.BooleanField(default=True)
    input_type=models.CharField(
        max_length=3,
        choices=InputType.choices,
        default=InputType.NUMERIC)
    position = models.FloatField(
        default=1.0, 
        help_text="The order of the question (e.g., 1.0, 1.5, 2.0)"
    )

    class Meta:
        ordering=['position']
        

    
    def __str__(self):
        surveys=",".join([s.name for s in self.survey.all()])
        return f'{surveys}-{self.subcategory.category.name}-{self.subcategory.name}-{self.code}'
    



