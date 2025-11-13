from rest_framework.decorators import api_view
from category.models import Category
from rest_framework import status,request,response,viewsets
from surveysession.models import Surveysession
from question.models import Question
from subcategory.models import Subcategory
from category.serializer import CategorySerializer
from question.serializer import QuestionSerializer
from surveysession.models import Surveysession
from survey.models import Survey
from response.models import Response
from visit.models import Visit


class CategoryViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing survey sessions.
    This provides `list`, `create`, `retrieve`, `update`,
    and `destroy` actions automatically.
    """
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer



@api_view(['GET'])
def get_categories(request):

    surveysession_id=request.GET.get('surveysession_id',None)
    
    if surveysession_id  in [None,'undefined']:
        return response.Response({'message':'invalid params id in get_categories'},status=status.HTTP_400_BAD_REQUEST)
    
    

    try:

        surveysession=Surveysession.objects.get(id=surveysession_id)
        survey=surveysession.survey
        questions=Question.objects.filter(survey=survey)

        categories=Category.objects.filter(subcategory__question__in=questions).distinct()

        res=CategorySerializer(categories,many=True)
        
        return response.Response(res.data,status=status.HTTP_200_OK)

    except Exception as e:
        return response.Response({'message': 'An error occurred', 'error': str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def questions_of_category_completed(request):

    category_id=request.GET.get('category_id')
    visit_id=request.GET.get('visit_id')

    if not category_id or not visit_id:
        return response.Response(
            {'error': 'Both category_id and visit_id are required parameters.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        visit=Visit.objects.get(id=visit_id)
        survey=visit.surveysession.survey
        num_original_questions_by_category=Question.objects.filter(subcategory__category__id=category_id,survey=survey,is_required=True).exclude(question_type='matrix_parent').count()
        num_original_q_debug=Question.objects.filter(subcategory__category__id=category_id,survey=survey,is_required=True).exclude(question_type='matrix_parent')
        print('original_q',num_original_questions_by_category)
        for q in num_original_q_debug:
            print(f'question_id={q.id}, question_code={q.code}')
        
        num_responses_related_category_id=Response.objects.filter(visita=visit_id,question__subcategory__category__id=category_id,question__is_required=True).count()
        num_responses_debug=Response.objects.filter(visita=visit_id,question__subcategory__category__id=category_id,question__is_required=True)
        print('num_resp',num_responses_related_category_id)
        for q in num_responses_debug:
            print(f'question_id={q.id}, question_code={q.code}')
        
        result=(num_original_questions_by_category > 0 and   num_original_questions_by_category==num_responses_related_category_id)

        return response.Response({'is_completed':result},status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return response.Response({'message':'an error ocurred in question_of_category_completed','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    










