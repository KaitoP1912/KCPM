from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/', include('accounts.urls')),

    path('api/households/', include('households.urls')),

    path('api/expenses/', include('expenses.urls')),

    path('api/notifications/', include('notifications.urls')),
]