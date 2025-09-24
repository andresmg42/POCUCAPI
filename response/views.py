from django.http import HttpResponse
from rest_framework import status,response
from rest_framework.decorators import api_view
from .serializer import ResponseSerializer
from .models import Response

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

@api_view(['POST'])
def create_response(request):
    data=request.data

    print(data)
    responses=[]
    raw_responses=[]

    try:

        for question_id,answer in data.items():
            new_res={'question':question_id,
                    'option':answer.get('optionId'),
                    'visita':answer.get('visitId'),
                    'numeric_value':answer.get('numeric_value'),
                    'text_value':answer.get('textValue')
                    }
            raw_responses.append(new_res)
            
        serializer=ResponseSerializer(data=raw_responses,many=True)

        if serializer.is_valid():
                
            validated_data=serializer.validated_data

            objects_to_create=[Response(**data) for data in validated_data]

            Response.objects.bulk_create(objects_to_create,ignore_conflicts=True)


            return response.Response({'message':'Response created successfully'},status=status.HTTP_201_CREATED)
                
        else:
            return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError) as e:
        return response.Response({'message': 'Invalid numeric value provided.', 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)   
    
    except Exception as e:
        return response.Response({'message':'error in crate response','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)