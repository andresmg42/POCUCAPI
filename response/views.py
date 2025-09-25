from django.http import HttpResponse
from rest_framework import status,response
from rest_framework.decorators import api_view
from .serializer import ResponseSerializer
from .models import Response
from surveysession.models import Surveysession
from survey.models import Survey
from visit.models import Visit

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['POST'])
def create_response(request):
    data=request.data

    print(data)
    responses=[]
    raw_responses=[]

    try:

        if not data:
            return response.Response({'message':'requested body can not be empty'},status=status.HTTP_400_BAD_REQUEST)

        for question_id,answer in data.items():
            new_res={'question':question_id,
                    'option':answer.get('optionId'),
                    'visita':answer.get('visitId'),
                    'numeric_value':answer.get('numeric_value'),
                    'text_value':answer.get('textValue')
                    }
            raw_responses.append(new_res)
            

        visit_id=raw_responses[0]['visita']

        serializer=ResponseSerializer(data=raw_responses,many=True)

        if serializer.is_valid():
                
            validated_data=serializer.validated_data


            objects_to_create=[Response(**data) for data in validated_data]

            Response.objects.bulk_create(objects_to_create,ignore_conflicts=True)


            if validate_visit_is_completed(validated_data,visit_id):

               Visit.objects.filter(id=visit_id).update(complete=True)

            return response.Response({'message':'Responses created successfully'},status=status.HTTP_201_CREATED)
                
        else:
            return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError) as e:
        return response.Response({'message': 'Invalid numeric value provided.', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)   
    
    except Exception as e:
        return response.Response({'message':'error in crate response','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def validate_visit_is_completed(data,visit_id):

    if not data:
        return False
    
    answered_questions_ids={response['question'] for response in data}

    try:
        visit=Visit.objects.select_related('surveysession__survey').get(id=visit_id)
    
    except Visit.DoesNotExist:
        return False

    required_questions_ids=set(visit.surveysession.survey.questions.values_list('id',flat=True))
    
    return required_questions_ids.issubset(answered_questions_ids)

   


