from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserProfileForm

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('userprofile:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    return render(request, 'userprofile/profile.html', {
        'form': form,
        'user': request.user
    })
