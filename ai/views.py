from django.shortcuts import render

# Create your views here.
def ai_view(request):
    return render(request, 'ai/ai.html')
