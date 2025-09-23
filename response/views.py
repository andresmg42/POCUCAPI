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

    try:

        for question in data.keys():
            new_res={'question':question,
                    'option':data[question]['optionId'],
                    'visita':data[question]['visitId'],
                    'numeric_value':int(data[question]['numeric_value']) if data[question]['numeric_value'] is not None else None,
                    'text_value':data[question]['textValue']
                    }
            
            serializer=ResponseSerializer(data=new_res)

            if serializer.is_valid():
                
                validated_data=serializer.validated_data

                obj,created=Response.objects.get_or_create(**validated_data)

                if created:
                    new_serializer=ResponseSerializer(obj)
                    responses.append(new_serializer.data)
                    
                else:
                    return response.Response({'message':'this response already exists'},status=status.HTTP_400_BAD_REQUEST)
            else:
                return response.Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        return response.Response({'message':'new responses created successfully','response':responses},status=status.HTTP_200_OK)
        
    except Exception as e:
        return response.Response({'message':'error in crate response','error':str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)