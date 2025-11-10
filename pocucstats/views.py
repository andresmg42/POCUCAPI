from django.shortcuts import render

# In your app's views.py
from django.db.models import Count, Avg, Min, Max,Q,CharField,F
from rest_framework.views import APIView
from rest_framework import response,status
from question.models import Question
from response.models import Response
from survey.models import Survey
from surveysession.models import Surveysession
from option.models import Option
from django.db.models.functions import Cast



class SurveyDashboardView(APIView):
    

    def get(self, request, format=None):
        
        question_id = request.GET.get('question_id')
        zone_id = request.GET.get('zone_id')
        survey_id=request.GET.get('survey_id')
        
        
       
        if not question_id:
           
            return response.Response(
                {'message': 'question_id is a required parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
           
           
            
            question = Question.objects.filter(id=question_id,survey=survey_id).first()

            
        except Exception as e:
           
            print(e) 
            return response.Response(
                {'message': 'An unexpected error occurred'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        

        if not question:
            return response.Response({'message':'questions not fount'},status=status.HTTP_404_NOT_FOUND)
        
        visual_data = self.get_visual_data_for_question(question,zone_id,survey_id)
        

        if visual_data:
            
            return response.Response(visual_data, status=status.HTTP_200_OK)
        else:
           
            return response.Response(
                {'message': f'Visualization for question type {question.question_type} is not implemented.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
                
                
        



    def get_visual_data_for_question(self, question: Question, zone_id=None,survey_id=1):
        """Dispatcher function to generate data based on question type."""

        if question.question_type == 'unique_response':

            response_filters = Q(question=question, visita__surveysession__survey_id=survey_id)
            if zone_id:
                response_filters &= Q(visita__surveysession__zone_id=zone_id)
            response_queryset = Response.objects.filter(response_filters)

            # 1. Get aggregate stats (this is fine)
            aggregate_data = response_queryset.aggregate(
                average=Avg('numeric_value'),
                minimum=Min('numeric_value'),
                maximum=Max('numeric_value'),
                count=Count('numeric_value'),
                count_text=Count('text_value')
            )

            # 2. Define your main 'numeric' query ONCE
            response_query_number = response_queryset.filter(
                numeric_value__isnull=False
            ).annotate(
                 description=Cast('numeric_value',output_field=CharField())
            ).values(
                'description'
            ).annotate(
                count=Count('description')
            ).order_by('-count')

            # 3. Define your main 'text' query ONCE
            response_query_text = response_queryset.filter(
                text_value__isnull=False
            ).annotate(
                 description=F('text_value')
                 
            ).values(
                'description'
            ).annotate(
                count=Count('description')
            ).order_by('-count')

            # 4. REUSE those queries
            aggregate_data['mode_numeric'] = response_query_number.first()
            aggregate_data['mode_text'] = response_query_text.first()
            
            aggregate_data['description'] = question.description if len(question.description) < 15 else question.code

            return {
                'id': question.id,
                'description': question.description,
                'question_code': question.code,
                'aggregate_stats': [aggregate_data],
                'visualization_type': 'bar_chart',
                # And just slice your existing queries for the data
                'data_numeric': list(response_query_number[:6]),  # <-- REUSE
                'data_text': list(response_query_text[:6])        # <-- REUSE
            }

        elif question.question_type == 'matrix_parent':
            final_numeric_data = []
            final_text_data=[]
            final_aggregate_data = []
            child_questions = question.child_questions.all().order_by('code')


            for child in child_questions:
                
                child_response_filters = Q(question=child,visita__surveysession__survey_id=survey_id)
                if zone_id:
                    child_response_filters &= Q(visita__surveysession__zone_id=zone_id)
                child_response_queryset = Response.objects.filter(child_response_filters)

                
                options_data_numeric_value = {'name': child.description}

                options_data_text_value={'name':child.description}
                

                
                response_counts_numeric_value = child_response_queryset.filter(numeric_value__isnull=False).annotate(
                     description=Cast('numeric_value',output_field=CharField())
                ).values(
                    'description'
                ).annotate(
                    count=Count('description') 
                ).order_by('-count')

                response_counts_text_value = child_response_queryset.filter(text_value__isnull=False).values(
                    'text_value'
                ).annotate(
                    count=Count('text_value') 
                ).order_by('-count')

                for item in response_counts_numeric_value[:6]:
                    
                        options_data_numeric_value[str(item['description'])] = item['count']

                
                for item in response_counts_text_value[:6]:
                            
                        options_data_text_value[item['text_value']]=item['count']

                # 4. Get aggregate stats FOR THIS CHILD.
                # FIX 4: Removed 'filter=count_filter'. Queryset is already filtered.
                aggregate_data = child_response_queryset.aggregate(
                    average=Avg('numeric_value'),
                    minimum=Min('numeric_value'),
                    maximum=Max('numeric_value'),
                    count=Count('numeric_value'),
                    count_text=Count('text_value')
                )
                
                aggregate_data['mode_numeric'] = response_counts_numeric_value.first()
                aggregate_data['mode_text']= response_counts_text_value.first()
                aggregate_data['description'] = child.description 

                final_numeric_data.append(options_data_numeric_value)
                if len(list(response_counts_text_value))!=0:
                    final_text_data.append(options_data_text_value)
                final_aggregate_data.append(aggregate_data)

            return {
                'id': question.id,
                'description': question.description,
                'question_code': question.code,
                'visualization_type': 'stacked_bar_100_percent',
                'aggregate_stats': final_aggregate_data,
                'data_numeric': final_numeric_data,
                'data_text':final_text_data
            }
                     
        
