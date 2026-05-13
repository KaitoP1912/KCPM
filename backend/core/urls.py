from django.contrib import admin
from django.urls import path, include

from core.views import health_check


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', health_check),
    path('api/auth/', include('accounts.urls')),
    path('api/households/',include('households.urls')),
    path('api/expenses/', include('expenses.urls')),
]