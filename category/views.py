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
from zone.models import Zone


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
    surveysession_id = request.GET.get('surveysession_id')
    
    # 1. Basic Validation
    if not surveysession_id or surveysession_id == 'undefined':
        return response.Response(
            {'message': 'Invalid params: surveysession_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # 2. Get relationships (use select_related for performance)
        surveysession = Surveysession.objects.select_related('zone', 'survey').get(id=surveysession_id)
        zone = surveysession.zone
        survey = surveysession.survey

        # 3. Define Allowed Zone Types
        # Logic: Always include Universal (None) and the specific Zone Type.
        # If the Zone is MIXED, we might want to include OPEN and CLOSED categories too.
        
        allowed_types = [zone.zone_type, None] # 'None' captures NULL/Universal categories
        
        # SPECIAL CASE: If the physical zone is MIXED, it usually contains 
        # both Open and Closed spaces, so we should allow those categories too.
        if zone.zone_type == Zone.ZoneType.MIXED:
            allowed_types.extend([Zone.ZoneType.OPEN, Zone.ZoneType.CLOSED])
        
        # 4. Filter Questions 
        # (Assuming standard ManyToMany relationship, otherwise check your model)
        questions = survey.questions.all()

        # 5. Filter Categories
        # We filter categories that contain the relevant questions AND match the zone type
        categories = Category.objects.filter(
            subcategory__question__in=questions,
            target_zone_type__in=allowed_types
        ).distinct()

        res = CategorySerializer(categories, many=True)
        return response.Response(res.data, status=status.HTTP_200_OK)

    except Surveysession.DoesNotExist:
        return response.Response(
            {'message': 'Survey Session found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return response.Response(
            {'message': 'An error occurred', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def questions_of_category_completed(request):
    category_id = request.GET.get('category_id')
    visit_id = request.GET.get('visit_id')

    # 1. Validation
    if not category_id or not visit_id:
        return response.Response(
            {'error': 'Both category_id and visit_id are required.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        visit = Visit.objects.select_related('surveysession__zone', 'surveysession__survey').get(id=visit_id)
        zone = visit.surveysession.zone
        survey = visit.surveysession.survey

        # 2. Logic: Define Allowed Zone Types (Universal + Specific)
        allowed_types = [zone.zone_type, None] 
        if zone.zone_type == Zone.ZoneType.MIXED:
            allowed_types.extend([Zone.ZoneType.OPEN, Zone.ZoneType.CLOSED])

        # 3. Get REQUIRED Questions IDs
        # We only want the IDs (values_list) to compare sets later
        required_questions_ids = set(survey.questions.filter(
            subcategory__category__id=category_id,
            is_required=True,
            subcategory__category__target_zone_type__in=allowed_types
        ).exclude(question_type='matrix_parent').values_list('id', flat=True))

        total_required = len(required_questions_ids)

        # Optimization: If there are no required questions in this category, 
        # is it considered "complete"? Usually YES.
        if total_required == 0:
            return response.Response({'is_completed': True}, status=status.HTTP_200_OK)

        # 4. Get Actual Responses
        # We filter responses that belong to this visit AND belong to the required list we just found.
        # We use .values_list('question_id') to see WHICH questions were answered.
        answered_questions_ids = set(Response.objects.filter(
            visita=visit, # Note: Check if your model field is 'visit' or 'visita'
            question_id__in=required_questions_ids
        ).values_list('question_id', flat=True))

        # 5. Compare Sets
        # This ensures that if 5 questions are required, we have responses for those exact 5 questions.
        # This prevents bugs where duplicate answers to Q1 make the count look correct while Q2 is missing.
        is_completed = required_questions_ids == answered_questions_ids

        return response.Response({'is_completed': is_completed}, status=status.HTTP_200_OK)

    except Visit.DoesNotExist:
         return response.Response({'error': 'Visit not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error: {e}")
        return response.Response(
            {'message': 'An error occurred', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    










