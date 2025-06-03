from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import FAQ, FAQSubQuestion
from csa.models import CSA
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST



DEFAULT_FAQID = "default-app-faq"

# Create your views here.

@login_required
def faq_list(request, content_type_id, object_id):
    """Render the FAQ list for a specific object"""
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    obj = get_object_or_404(model_class, id=object_id)
    
    faqs = FAQ.objects.filter(
        content_type=content_type,
        object_id=object_id,
        is_active=True
    ).prefetch_related('sub_questions')
    
    return render(request, 'faq_management/faq_list.html', {
        'object': obj,
        'faqs': faqs,
        'content_type_id': content_type_id,
        'object_id': object_id
    })




@login_required
@require_POST
@csrf_exempt
def create_faq(request):
    """Create a new FAQ for a given faqid (or default)."""
    try:
        data = json.loads(request.body)
        faqs_data = data.get('faqs', [])
        faqid = data.get('faqid') or request.POST.get('faqid') or DEFAULT_FAQID

        
        # Save new FAQs
        for faq_data in faqs_data:
            faq = FAQ.objects.create(
                faqid=faqid,
                question=faq_data['question'],
                response_type=faq_data['response_type'],
                answer=faq_data.get('answer', '')
            )
            # Save sub-questions if any
            for i, sub_q in enumerate(faq_data.get('sub_questions', [])):
                FAQSubQuestion.objects.create(
                    faq=faq,
                    question=sub_q['question'],
                    answer=sub_q['answer'],
                    order=i
                )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)




@login_required
@require_http_methods(['POST'])
@csrf_exempt
def save_faqs(request):
    """update FAQs for a given using its id"""
    try:
        data = json.loads(request.body)
        faqs_data = data.get('faqs', [])
        faqid = data.get('faqid') or request.POST.get('faqid') or DEFAULT_FAQID

        # Remove existing FAQs for this faqid
        FAQ.objects.filter(faqid=faqid).delete()

        # Save new FAQs
        for faq_data in faqs_data:
            faq = FAQ.objects.create(
                faqid=faqid,
                question=faq_data['question'],
                response_type=faq_data['response_type'],
                answer=faq_data.get('answer', '')
            )
            # Save sub-questions if any
            for i, sub_q in enumerate(faq_data.get('sub_questions', [])):
                FAQSubQuestion.objects.create(
                    faq=faq,
                    question=sub_q['question'],
                    answer=sub_q['answer'],
                    order=i
                )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_http_methods(['DELETE'])
def delete_faq(request, faq_id):
    """Soft delete a FAQ"""
    faq = get_object_or_404(FAQ, id=faq_id)
    faq.is_active = False
    faq.save()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(['GET'])
def get_faq(request, faq_id):
    """Get a single FAQ with its sub-questions"""
    faq = get_object_or_404(FAQ, id=faq_id)
    sub_questions = list(faq.sub_questions.values('id', 'question', 'answer', 'order'))
    
    return JsonResponse({
        'id': faq.id,
        'question': faq.question,
        'response_type': faq.response_type,
        'answer': faq.answer,
        'sub_questions': sub_questions
    })

@login_required
def test_faq_system(request):
    """Test view for the FAQ management system"""
    # Get content types
    csa_content_type = ContentType.objects.get_for_model(CSA)
    user_content_type = ContentType.objects.get_for_model(request.user.__class__)
    
    # Get a CSA for testing (you might want to modify this based on your needs)
    csa = CSA.objects.first()
    
    context = {
        'csa_content_type': csa_content_type,
        'user_content_type': user_content_type,
        'csa': csa,
        'user': request.user,
    }
    
    return render(request, 'faq_management/test.html', context)

@login_required
def faq_template(request):
    """Render the FAQ template without requiring content type or object ID."""
    return render(request, 'faq_management/faq_template.html')

@login_required
@require_http_methods(['GET'])
def list_faqs(request):
    """Return a list of FAQs for a given faqid (or default)."""
    faqid = request.GET.get('faqid') or DEFAULT_FAQID
    faqs = FAQ.objects.filter(faqid=faqid, is_active=True).prefetch_related('sub_questions')
    faqs_list = []
    for faq in faqs:
        faqs_list.append({
            'id': faq.id,
            'question': faq.question,
            'response_type': faq.response_type,
            'answer': faq.answer,
            'sub_questions': [
                {
                    'id': sq.id,
                    'question': sq.question,
                    'answer': sq.answer,
                    'order': sq.order
                } for sq in faq.sub_questions.all()
            ]
        })
    return JsonResponse({'faqs': faqs_list})

@login_required
def get_faqs_by_faqid(request, faqid):
    """
    Returns FAQs for a specific faqid in a format suitable for accordion display
    """
    try:
        # Use DEFAULT_FAQID if faqid is 'default'
        if faqid == 'default':
            faqid = DEFAULT_FAQID

        faqs = FAQ.objects.filter(
            faqid=faqid,
            is_active=True
        ).prefetch_related('sub_questions').order_by('created_at')
        
        return render(request, 'faq_management/faqs.html', {
            'faqs': faqs,
            'faqid': faqid
        })
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_faqs_by_faqid: {str(e)}")
        return JsonResponse({
            'error': 'An error occurred while fetching FAQs',
            'details': str(e)
        }, status=500)

@login_required
@require_http_methods(['POST'])
def update_faq(request, faq_id):
    """Update a single FAQ and its sub-questions"""
    try:
        faq = get_object_or_404(FAQ, id=faq_id)
        data = json.loads(request.body)
        
        # Update FAQ
        faq.question = data['question']
        faq.response_type = data['response_type']
        faq.answer = data.get('answer', '')
        faq.save()
        
        # Update sub-questions if any
        if data['response_type'] == 'subquestions':
            # Remove existing sub-questions
            faq.sub_questions.all().delete()
            
            # Add new sub-questions
            for i, sub_q in enumerate(data.get('sub_questions', [])):
                FAQSubQuestion.objects.create(
                    faq=faq,
                    question=sub_q['question'],
                    answer=sub_q['answer'],
                    order=i
                )
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

