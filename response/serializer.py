from rest_framework import serializers
from .models import Response
from .models import QuestionCommentAnswer


class ResponseSerializer(serializers.ModelSerializer):
    numeric_value = serializers.IntegerField(required=False, allow_null=True)
    observer= serializers.ReadOnlyField(source='visita.surveysession.observer.name')
    observer_email= serializers.ReadOnlyField(source='visita.surveysession.observer.email')
    surveysession_id= serializers.ReadOnlyField(source='visita.surveysession.id')
    survey= serializers.ReadOnlyField(source='visita.surveysession.survey.name')
    zone= serializers.ReadOnlyField(source='visita.surveysession.zone.name')
    campus= serializers.ReadOnlyField(source='visita.surveysession.zone.campus.name')
    question_description= serializers.ReadOnlyField(source='question.description')
    category= serializers.ReadOnlyField(source='question.subcategory.category.name')
    subcategory= serializers.ReadOnlyField(source='question.subcategory.name')
    observer_id= serializers.ReadOnlyField(source='visita.surveysession.observer.id')
    survey_id= serializers.ReadOnlyField(source='visita.surveysession.survey.id')
    zone_id= serializers.ReadOnlyField(source='visita.surveysession.zone.id')
    campus_id= serializers.ReadOnlyField(source='visita.surveysession.zone.campus.id')
    subcategory_id= serializers.ReadOnlyField(source='question.subcategory.id')
    category_id= serializers.ReadOnlyField(source='question.subcategory.category.id')
    parent_question=serializers.ReadOnlyField(source='question.parent_question.description')
    parent_question_id=serializers.ReadOnlyField(source='question.parent_question.id')
    question_code=serializers.ReadOnlyField(source='question.code')
    
    class Meta:
        model=Response
        fields=['id','option','visita','question','numeric_value',
                'text_value','surveysession_id','survey','zone','campus',
                'question_description','category','subcategory',
                'observer','observer_email','observer_id','survey_id','zone_id',
                'campus_id','subcategory_id','category_id','parent_question','parent_question_id','question_code']
    

class QuestionCommentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model=QuestionCommentAnswer
        fields='__all__'
