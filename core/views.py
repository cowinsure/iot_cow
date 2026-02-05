from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Profile, Cow
from .serializers import ProfileSerializer, CowSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import logging

logger = logging.getLogger(__name__)

# List & Create
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile_list(request):
    if request.method == 'GET':
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True, context={'request': request})
        return Response(serializer.data)
    
    if request.method == 'POST':
        serializer = ProfileSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Retrieve, Update, Delete
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
    
    if request.method in ['PUT', 'PATCH']:
        serializer = ProfileSerializer(profile, data=request.data, partial=(request.method=='PATCH'), context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        profile.delete()
        return Response({"message": "Profile deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# Endpoint to receive cow collar data from ESP32
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def cow_data(request):
    """
    POST endpoint for receiving cow collar data from ESP32 devices.
    Expects JSON data with cow sensor information.
    """
    data = request.data
    
    if not data:
        return Response(
            {"status": "error", "message": "No JSON received"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Log received data
    logger.info("=== Cow Collar Data Received ===")
    
    logger.info(f"Data: {data}")
    logger.info("===============================")
    
    # Extract cow_id from data (required)
    cow_id = data.get('cow_id')
    if not cow_id:
        return Response(
            {"status": "error", "message": "cow_id is required"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create new cow record (allow duplicate cow_id)
    cow = Cow.objects.create(
        cow_id=cow_id,
        temperature=data.get('temperature'),
        heart_rate=data.get('heart_rate'),
        activity_level=data.get('activity_level'),
        battery_level=data.get('battery_level'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        raw_data=data,
    )
    
    return Response(
        {"status": "ok", "message": "Cow data saved successfully"},
        status=status.HTTP_200_OK
    )


# List all cows or get specific cow
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def cow_list(request):
    """
    GET endpoint to retrieve cow data.
    Returns all cows if no cow_id specified.
    Returns specific cow if cow_id provided as query param.
    """
    cow_id = request.query_params.get('cow_id')
    
    if cow_id:
        cow = get_object_or_404(Cow, cow_id=cow_id)
        serializer = CowSerializer(cow)
        return Response(serializer.data)
    
    cows = Cow.objects.all().order_by('-timestamp')
    serializer = CowSerializer(cows, many=True)
    return Response(serializer.data)
