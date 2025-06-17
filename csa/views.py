from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.db import transaction
import firebase_admin
from firebase_admin import credentials, db
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
            # Extract FAQs from request data
            faqs_data = data.pop('faqs', [])
            print("FAQS DATA: ", faqs_data)
            
            # Create CSA in Django
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            csa = serializer.save(user=request.user)
            
            # Associate CSA with all of the user's active teams
            from team.models import Team
            user_teams = Team.objects.filter(members__user=request.user, members__is_active=True)
            csa.teams.add(*user_teams)
            
            # Generate Firebase path
            firebase_path = firebase_generate_path(request.user, csa.id)
            csa.firebase_path = firebase_path
            csa.save()
            
            firebase_save_faqs(request.user, csa.id, faqs_data)
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
            # Generate Firebase path
            firebase_path = firebase_generate_path(request.user, csa.id)
            csa.firebase_path = firebase_path
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
            # Initialize Firebase first
            firebase_init()
            
            # Handle file uploads, URLs, and text
            knowledge_data = request.data
            
            # Save to Firebase or your preferred storage
            firebase_path = csa.firebase_path
            ref = db.reference(firebase_path)
            ref.update({
                'knowledge_base': knowledge_data
            })
            
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
            # Extract FAQs from request data
            faqs_data = request.data.get('faqs', [])
            
            # Save FAQs to Firebase
            firebase_save_faqs(request.user, csa.id, faqs_data)
            
            # Handle platform connections and CRM data
            integrations_data = request.data.get('integrations', {})
            firebase_path = csa.firebase_path
            ref = db.reference(firebase_path)
            ref.update({
                'integrations': integrations_data
            })
            
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
            
            # Delete Firebase data
            firebase_delete_agent(request.user, csa.id)
            
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
    # Fetch FAQs from Firebase if needed
    faqs = firebase_get_faqs(csa.firebase_path) if csa.firebase_path else []
    faqs_json = json.dumps(faqs)
    return render(request, 'csa/create.html', {'csa': csa, 'is_edit': True, 'faqs': faqs_json})

def crm_connect(request):
    # You can add logic here to show available CRMs, connection status, etc.
    return render(request, 'csa/crm_connect.html')  

@require_GET
def csa_faqs_api(request, pk):
    csa = get_object_or_404(CSA, pk=pk, user=request.user)
    faqs = firebase_get_faqs(csa.firebase_path)
    return JsonResponse({'faqs': faqs})

def firebase_generate_path(user, csa_id):
    """Return the Firebase path for a user's CSA agent."""
    return f"users/{user.username}/agents/{csa_id}"

def firebase_init():
    """Initialize Firebase if not already initialized."""
    import firebase_admin
    from firebase_admin import credentials
    from django.conf import settings
    import os

    if not firebase_admin._apps:
        cred_path = os.path.join(settings.BASE_DIR, 'csa-1a82c-firebase-adminsdk-fbsvc-5f3d988418.json')
        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Firebase credentials file not found at: {cred_path}")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://csa-1a82c-default-rtdb.firebaseio.com/'
        })

def firebase_save_faqs(user, csa_id, faqs_data):
    """Save FAQs to Firebase under the agent's path."""
    from firebase_admin import db
    firebase_init()
    firebase_path = firebase_generate_path(user, csa_id)
    ref = db.reference(firebase_path)
    # Always create the agent node
    ref.set({'faqs': {}})
    faqs_ref = ref.child('faqs')
    for faq_data in faqs_data:
        faq_ref = faqs_ref.push()
        faq_ref.set({
            'question': faq_data['question'],
            'response_type': faq_data['response_type'],
            'answer': faq_data.get('answer', ''),
            'sub_questions': faq_data.get('sub_questions', [])
        })

def firebase_delete_agent(user, csa_id):
    """Delete the agent's record from Firebase."""
    from firebase_admin import db
    firebase_init()
    firebase_path = firebase_generate_path(user, csa_id)
    ref = db.reference(firebase_path)
    ref.delete()

def firebase_get_faqs(firebase_path):
    """Fetch FAQs from Firebase for a given agent path."""
    from firebase_admin import db
    firebase_init()
    ref = db.reference(firebase_path + '/faqs')
    faqs_dict = ref.get() or {}
    faqs = []
    for key, value in faqs_dict.items():
        value['id'] = key
        faqs.append(value)
    return faqs

