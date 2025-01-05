from django.shortcuts import render

# Create your views here.
def assistant(request):
    return render(request, 'assistant/assistant.html')

def get_emails(request):
    pass