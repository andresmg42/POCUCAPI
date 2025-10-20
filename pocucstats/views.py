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
        
        question_id = request.GET.get('question_id')
        zone_id = request.GET.get('zone_id')
        # survey_id=request.GET.get('survey_id')
        
       
        if not question_id:
           
            return response.Response(
                {'message': 'question_id is a required parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
           
            query_params = {
                'id': question_id, 
                
            }
            if zone_id:
                query_params['survey__sessions__zone_id'] = zone_id
            
            
            question = Question.objects.filter(**query_params).first()

            
        except Exception as e:
           
            print(e) 
            return response.Response(
                {'message': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        

        if not question:
            return response.Response({'message':'questions not fount'},status=status.HTTP_404_NOT_FOUND)
        
        visual_data = self.get_visual_data_for_question(question)
        



        
        
        
        if visual_data:
            
            return response.Response(visual_data, status=status.HTTP_200_OK)
        else:
           
            return response.Response(
                {'message': f'Visualization for question type {question.question_type} is not implemented.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
                
                
        

    def get_visual_data_for_question(self, question:Question):
        """Dispatcher function to generate data based on question type."""
        
        
        if question.question_type == 'unique_response':
            
            data = question.options.all().annotate(
                response_count=Count('response')
            ).values('description', 'response_count')
            
            return {
                'id':question.id,
                'description':question.description,
                'question_code': question.code,
                
                'visualization_type': 'bar_chart',
                'data': list(data) 
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
                     
        
