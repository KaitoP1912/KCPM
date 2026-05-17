from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import (
    RegisterView,
    SaveFCMTokenView,
    UserProfileView,
)


urlpatterns = [
    path('register/', RegisterView.as_view()),

    path('login/', TokenObtainPairView.as_view()),

    path('refresh/', TokenRefreshView.as_view()),

    path('profile/', UserProfileView.as_view()),

    path('save-fcm-token/', SaveFCMTokenView.as_view()),
]