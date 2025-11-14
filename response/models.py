from django.db import models
from option.models import Option
from visit.models import Visit
from question.models import Question

class Response(models.Model):
    option=models.ForeignKey(Option,on_delete=models.CASCADE,null=True,related_name='response')
    visita=models.ForeignKey(Visit,on_delete=models.CASCADE)
    question=models.ForeignKey(Question,on_delete=models.CASCADE,related_name='reponses')
    numeric_value=models.IntegerField(null=True,blank=True)
    text_value=models.CharField(max_length=30,null=True,blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['visita','question'], 
                name='unique_response_by_visita_question_and_option'
            )
        ]
        

    def __str__(self):
        return f'survey:{self.visita.surveysession.survey.name}-session:{self.visita.surveysession.number_session}-visita:{self.visita.visit_number}-question:{self.question.__str__()}'

class QuestionCommentAnswer(models.Model):
    visita = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='comments')
    
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    
    
    comment = models.TextField()

    class Meta:
        constraints = [
            
            models.UniqueConstraint(
                fields=['visita', 'question'], 
                name='unique_comment_per_visit_question'
            )
        ]

    def __str__(self):
        return f'Comment by {self.visita} on {self.question}'