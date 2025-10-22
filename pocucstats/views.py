from django.shortcuts import render

# In your app's views.py
from django.db.models import Count, Avg, Min, Max,Q
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
        
        visual_data = self.get_visual_data_for_question(question,zone_id)
        

        if visual_data:
            
            return response.Response(visual_data, status=status.HTTP_200_OK)
        else:
           
            return response.Response(
                {'message': f'Visualization for question type {question.question_type} is not implemented.'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
                
                
        



    def get_visual_data_for_question(self, question: Question, zone_id=None):
        """Dispatcher function to generate data based on question type."""

        if question.question_type == 'unique_response':

            # 1. Base QuerySet for Aggregates & Mode (Filters for question and zone)
            response_filters = Q(question=question)
            if zone_id:
                response_filters &= Q(visita__surveysession__zone_id=zone_id)
            response_queryset = Response.objects.filter(response_filters)

            # 2. Filter for the 'data' annotation. This is different!
            # Your insight was correct: we must filter for this specific question.
            count_filter = Q(response__question=question)
            if zone_id:
                # FIX 1: Removed 'response__' prefix. Path is from the Response model.
                count_filter &= Q(response__visita__surveysession__zone_id=zone_id)
            
            data = question.options.all().annotate(
                # This now correctly counts responses for THIS option AND THIS question
                response_count=Count('response', filter=count_filter)
            ).values('description', 'response_count')

            # 3. Get aggregate stats. 
            # FIX 2: Removed 'filter=count_filter'. Queryset is already filtered.
            aggregate_data = response_queryset.aggregate(
                average=Avg('numeric_value'),
                minimum=Min('numeric_value'),
                maximum=Max('numeric_value'),
                count=Count('numeric_value')
            )

            # 4. Get the mode. 
            # FIX 2: Removed 'filter=count_filter'. Queryset is already filtered.
            mode_query = response_queryset.values('numeric_value').annotate(
                count=Count('numeric_value')
            ).order_by('-count')
            
            mode_result = mode_query.first()
            aggregate_data['mode'] = mode_result
            aggregate_data['description']=question.description if len(question.description)<15 else question.code

            return {
                'id': question.id,
                'description': question.description,
                'question_code': question.code,
                'aggregate_stats': [aggregate_data],
                'visualization_type': 'bar_chart',
                'data': list(data)
            }

        elif question.question_type == 'matrix_parent':
            final_data = []
            final_aggregate_data = []
            option_descriptions = list(question.options.all().values_list('description', flat=True))
            child_questions = question.child_questions.all().order_by('code')

            # FIX 3: This filter is for the annotation and only needs the zone.
            # The question=child filter is applied in the .filter() part below.
            count_filter = Q()
            if zone_id:
                count_filter = Q(visita__surveysession__zone_id=zone_id)

            for child in child_questions:
                # 1. Base QuerySet FOR THIS CHILD (Filters for child and zone)
                child_response_filters = Q(question=child)
                if zone_id:
                    child_response_filters &= Q(visita__surveysession__zone_id=zone_id)
                child_response_queryset = Response.objects.filter(child_response_filters)

                # 2. Prepare data for the matrix chart
                options_data = {'name': child.description}
                for desc in option_descriptions:
                    options_data[desc] = 0

                # 3. Get counts for this child, grouped by option.
                # We filter for the child first, then apply the (optional) zone filter
                # inside the annotation.
                response_counts = Response.objects.filter(question=child).values(
                    'option__description'
                ).annotate(
                    count=Count('id', filter=count_filter) 
                )

                for item in response_counts:
                    if item['option__description']:
                        options_data[item['option__description']] = item['count']

                # 4. Get aggregate stats FOR THIS CHILD.
                # FIX 4: Removed 'filter=count_filter'. Queryset is already filtered.
                aggregate_data = child_response_queryset.aggregate(
                    average=Avg('numeric_value'),
                    minimum=Min('numeric_value'),
                    maximum=Max('numeric_value'),
                    count=Count('numeric_value')
                )

                # 5. Get mode FOR THIS CHILD.
                # FIX 4: Removed 'filter=count_filter'. Queryset is already filtered.
                mode_query = child_response_queryset.values('numeric_value').annotate(
                    count=Count('numeric_value')
                ).order_by('-count')
                
                aggregate_data['mode'] = mode_query.first()
                aggregate_data['description'] = child.description 

                # 6. Assemble the final data for this child
                final_data.append(options_data)
                final_aggregate_data.append(aggregate_data)

            return {
                'id': question.id,
                'description': question.description,
                'question_code': question.code,
                'visualization_type': 'stacked_bar_100_percent',
                'aggregate_stats': final_aggregate_data,
                'data': final_data
            }
                     
        
