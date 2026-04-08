from rest_framework.decorators import api_view,permission_classes,parser_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Profile, Cow
from .serializers import ProfileSerializer, CowSerializer
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
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


# User registration
@api_view(['POST'])
def register_user(request):
    """
    Register a new user.
    Expects: username, password, email (optional), first_name, last_name
    """
    data = request.data

    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    first_name = data.get('first_name', '')
    last_name = data.get('last_name', '')

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if email and User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already exists"},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "tokens": {
                "access": access_token,
                "refresh": refresh_token
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


# User login
@api_view(['POST'])
def login_user(request):
    """
    Login user and return JWT tokens.
    Expects: username, password
    """
    data = request.data

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {"error": "User account is disabled"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return Response({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
        "tokens": {
            "access": access_token,
            "refresh": refresh_token
        }
    }, status=status.HTTP_200_OK)


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
        activity_status=data.get('activity_status'),
        battery_level=data.get('battery_level'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        gyro_x=data.get('gyro_x'),
        gyro_y=data.get('gyro_y'),
        gyro_z=data.get('gyro_z'),
        accel_x=data.get('accel_x'),
        accel_y=data.get('accel_y'),
        accel_z=data.get('accel_z'),
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
    Returns paginated cows if no cow_id specified.
    Returns specific cow if cow_id provided as query param.
    """
    from rest_framework.pagination import PageNumberPagination

    cow_id = request.query_params.get('cow_id')

    if cow_id:
        cow = get_object_or_404(Cow, cow_id=cow_id)
        serializer = CowSerializer(cow)
        return Response(serializer.data)

    cows = Cow.objects.all().order_by('-timestamp')

    # Apply pagination
    paginator = PageNumberPagination()
    paginator.page_size = request.query_params.get('page_size', 10)  # Allow custom page size
    result_page = paginator.paginate_queryset(cows, request)

    serializer = CowSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)
