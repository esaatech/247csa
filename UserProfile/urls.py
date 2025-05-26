from django.urls import path
from .views import *

app_name = 'UserProfile'

urlpatterns = [
    path('', UserProfileView.as_view(), name='user_profile'),
]