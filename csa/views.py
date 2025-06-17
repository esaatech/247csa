from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.db import transaction
from django.conf import settings
import os
from .models import CSA, FAQ, SubQuestion
from .serializers import CSASerializer, FAQSerializer, SubQuestionSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseServerError, JsonResponse
import json
from django.views.decorators.http import require_GET
import logging
from team.models import Team

logger = logging.getLogger(__name__)

def dashboard(request):
    user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
    csas = CSA.objects.filter(teams__in=user_teams).distinct().order_by('-created_at')
    csa_id = request.GET.get('csa_id')
    selected_csa = None
    if csa_id:
        try:
            selected_csa = csas.get(id=csa_id)
        except CSA.DoesNotExist:
            selected_csa = csas.first() if csas else None
    else:
        selected_csa = csas.first() if csas else None
    open_csa_id = str(selected_csa.id) if selected_csa else ''
    can_edit = selected_csa.can_edit(request.user) if selected_csa else False
    context = {
        'csas': csas,
        'selected_csa': selected_csa,
        'open_csa_id': open_csa_id,
        'csa_id': open_csa_id,
        'can_edit': can_edit,
    }
    return render(request, 'csa/csa-dashboard.html', context)

class CSAViewSet(viewsets.ModelViewSet):
    print("CSAViewSet called")
    serializer_class = CSASerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def get_queryset(self):
        from team.models import Team
        user_teams = Team.objects.filter(members__user=self.request.user, members__is_active=True)
        return CSA.objects.filter(teams__in=user_teams).distinct()
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("Creating CSA in create")
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )                      
        
        # Add user to the data
        data = request.data.copy()
        data['user'] = request.user.id
        
        try:
            # Create CSA in Django
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            csa = serializer.save(user=request.user)
            
            # Associate CSA with all of the user's active teams
            from team.models import Team
            user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
            csa.teams.add(*user_teams)
            csa.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # If anything fails, rollback CSA creation
            if 'csa' in locals():
                csa.delete()
            return Response(
                {'error': f'Failed to create CSA: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def step1(self, request):
        """Save basic CSA information (name and description)"""
        print("Creating CSA with step1...................")
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        data = request.data.copy()
        data['user'] = request.user.id
        
        try:
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            csa = serializer.save(
                user=request.user,
                status='draft'  # Set initial status to draft
            )
            # Associate CSA with all of the user's active teams
            from team.models import Team
            user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
            csa.teams.add(*user_teams)
            csa.save()
            
            return Response({
                'id': csa.id,
                'name': csa.name,
                'description': csa.description
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to create CSA: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def step2(self, request, pk=None):
        """Save knowledge base information"""
        print("Creating CSA with step2.....................................")
        csa = self.get_object()
        
        try:
            # Update status to in_progress
            csa.status = 'in_progress'
            csa.save()
            
            return Response({'success': True})
        except Exception as e:
            print(f"Error in step2: {str(e)}")
            return Response(
                {'error': f'Failed to save knowledge base: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def step3(self, request, pk=None):
        """Save integrations and FAQs"""
        print("Creating CSA with step3.................................")
        csa = self.get_object()
        
        try:
            # Update status to ready when all steps are complete
            csa.status = 'ready'
            csa.save()
            
            return Response({'success': True})
        except Exception as e:
            return Response(
                {'error': f'Failed to save integrations: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, *args, **kwargs):
        print("destroy called")
        try:
            # Get the CSA instance before deletion
            csa = self.get_object()
            
            # Delete related platform connections
            from platform_connections.models import WebsiteChatConnection, SMSConnection
            WebsiteChatConnection.objects.filter(agent_id=csa.id).delete()
            SMSConnection.objects.filter(agent_id=csa.id).delete()
            
            # Delete FAQs from Django DB
            from faq_management.models import FAQ
            FAQ.objects.filter(faqid=str(csa.id)).delete()
            
            # Delete the CSA
            self.perform_destroy(csa)
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            print(f"Error in CSA deletion: {str(e)}")
            return Response(
                {'error': f'Failed to delete CSA: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def csa_list(request):
    from team.models import Team
    user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
    csas = CSA.objects.filter(teams__in=user_teams).distinct().order_by('-created_at')
    return render(request, 'csa/csa_list.html', {'csas': csas})

def csa_create(request):
    print("csa_create called")
    if request.method == 'POST':
        # Handle POST request using the existing CSAViewSet
        viewset = CSAViewSet()
        viewset.request = request
        return viewset.create(request)
    else:
        # Handle GET request - show the form
        return render(request, 'csa/create.html')

def csa_detail(request, pk):
    from team.models import Team
    user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
    csa = get_object_or_404(CSA, id=pk, teams__in=user_teams)
    can_edit = csa.can_edit(request.user)
    return render(request, 'csa/detail.html', {'csa': csa, 'can_edit': can_edit})

def csa_edit(request, pk):
    from team.models import Team
    import json
    user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
    csa = get_object_or_404(CSA, id=pk, teams__in=user_teams)
    return render(request, 'csa/create.html', {'csa': csa, 'is_edit': True})

def crm_connect(request):
    # You can add logic here to show available CRMs, connection status, etc.
    return render(request, 'csa/crm_connect.html')  

@require_GET
def csa_faqs_api(request, pk):
    csa = get_object_or_404(CSA, pk=pk, user=request.user)
    faqs = FAQ.objects.filter(csa=csa)
    serializer = FAQSerializer(faqs, many=True)
    return JsonResponse({'faqs': serializer.data})

def welcome_message(request):
    return render(request, 'csa/welcome_message.html')

