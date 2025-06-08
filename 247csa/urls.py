from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('assistant/', include('assistant.urls')),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('auth/', include('authentication.urls')),
    path('UserProfile/', include('UserProfile.urls')),
    path('ai/', include('ai.urls')),
    path('api/csa/', include('csa.urls', namespace='csa')),
    path('platform_connections/', include('platform_connections.urls', namespace='platform_connections')),
    path('chatui/', include('chatui.urls', namespace='chatui')),
    path('faq/', include('faq_management.urls')),
    path('mycrm/', include('mycrm.urls')),
    path('task/', include('task.urls')),
    path('interaction/', include('interaction.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
