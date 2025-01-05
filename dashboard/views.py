from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Assistant, Instruction, Document, Channel

@login_required
def dashboard_view(request):
    return render(request, 'dashboard/dashboard.html')

@login_required
def assistant_list(request):
    assistants = Assistant.objects.filter(created_by=request.user)
    return render(request, 'dashboard/assistants.html', {'assistants': assistants})

@login_required
def create_assistant(request):
    if request.method == 'POST':
        try:
            # Create assistant
            assistant = Assistant.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description'),
                created_by=request.user
            )

            # Add instructions
            instructions = request.POST.getlist('instructions[]')
            for index, instruction in enumerate(instructions):
                if instruction:  # Only create if instruction is not empty
                    Instruction.objects.create(
                        assistant=assistant,
                        content=instruction,
                        order=index
                    )

            # Handle file uploads
            files = request.FILES.getlist('document')
            for file in files:
                Document.objects.create(
                    assistant=assistant,
                    file=file
                )

            messages.success(request, 'Assistant created successfully!')
            return redirect('dashboard:assistants')
        except Exception as e:
            messages.error(request, f'Error creating assistant: {str(e)}')
            return redirect('dashboard:dashboard')

    return render(request, 'dashboard/create_assistant.html')

@login_required
def integration_list(request):
    channels = Channel.objects.all()
    return render(request, 'dashboard/integrations.html', {'channels': channels})
