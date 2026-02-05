from django.urls import path
from .views import profile_detail, profile_list, cow_data, cow_list
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('profiles/', profile_list),
    path('profiles/<int:pk>/', profile_detail),
     # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Cow collar data endpoints
    path('api/cow-data/', cow_data, name='cow_data'),
    path('api/cows/', cow_list, name='cow_list'),
]