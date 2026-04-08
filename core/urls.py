from django.urls import path
from .views import profile_detail, profile_list, cow_data, cow_list, register_user, login_user
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # User authentication endpoints
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),

    # JWT token endpoints (alternative login method)
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Profile management
    path('profiles/', profile_list),
    path('profiles/<int:pk>/', profile_detail),

    # Cow collar data endpoints
    path('api/cow-data/', cow_data, name='cow_data'),
    path('api/cows/', cow_list, name='cow_list'),
]