from django.shortcuts import render
from django.views.generic import View
# Create your views here.
class UserProfileView(View):
    def get(self, request):
        return render(request, 'UserProfile/user_profile.html')