from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('auth/', include('authentication.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', include('home.urls')),
    path('UserProfile/', include('UserProfile.urls')),
    path('assistant/', include('assistant.urls')),
]
