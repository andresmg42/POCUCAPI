from django.shortcuts import render

# In your app's views.py
from django.db.models import Count, Avg, Min, Max
from rest_framework.views import APIView
from rest_framework import response,status
from question.models import Question
from response.models import Response
from survey.models import Survey
from surveysession.models import Surveysession
from option.models import Option



class SurveyDashboardView(APIView):
    def get(self, request, format=None):
        
        survey_id=request.GET.get('survey_id')
        zone_id=request.GET.get('zone_id')
        if zone_id and survey_id:
             
             questions = Question.objects.filter(survey__id=survey_id , survey__sessions__zone_id =zone_id).distinct()
        elif survey_id:
             questions = Question.objects.filter(survey__id=survey_id)
        else:
            return response.Response({'survey_id and zone_id invalid parameters'},status=status.HTTP_400_BAD_REQUEST)

        dashboard_layout = []
        for question in questions:
            # 2. Process each question based on its type
            visual_data = self.get_visual_data_for_question(question)
            if visual_data:
                dashboard_layout.append(visual_data)
                
        return response.Response(dashboard_layout,status=status.HTTP_200_OK)

    def get_visual_data_for_question(self, question:Question):
        """Dispatcher function to generate data based on question type."""
        
        # For multiple choice questions (bar chart)
        if question.question_type == 'unique_response':
            # Aggregate counts for each option
            data = question.options.all().annotate(
                response_count=Count('response')
            ).values('description', 'response_count')
            
            return {
                'id':question.id,
                'description':question.description,
                'question_code': question.code,
                # 'question_text': question.description,
                'visualization_type': 'bar_chart',
                'data': list(data) # e.g., [{'description': 'Yes', 'response_count': 50}, ...]
            }

        
        elif question.question_type == 'matrix_parent':  

            final_data=[]

            option_descriptions=list(question.options.all().values_list('description',flat=True))       

            child_questions=question.child_questions.all().order_by('code')

            for child in child_questions:
                 
                child_data = {'name':child.description}
                for desc in option_descriptions:
                 child_data[desc]=0

                

                response_counts=Response.objects.filter(question=child).values(
                    'option__description'
                ).annotate(
                    count=Count('id')
                )

                for item in response_counts:
                    child_data[item['option__description']]=item['count']

                final_data.append(child_data)

            return {
                'id':question.id,
                'description':question.description,
                # 'question_parent_text':question.description,
                'question_code':question.code,
                'visualization_type':'stacked_bar_100_percent',
                'data':final_data
                
            }
                     
        
