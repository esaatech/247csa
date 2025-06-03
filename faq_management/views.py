from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from .models import FAQ, FAQSubQuestion
from csa.models import CSA
import json

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
@require_http_methods(['POST'])
def save_faqs(request, content_type_id, object_id):
    """Save or update FAQs for an object"""
    content_type = get_object_or_404(ContentType, id=content_type_id)
    model_class = content_type.model_class()
    obj = get_object_or_404(model_class, id=object_id)
    
    try:
        data = json.loads(request.body)
        faqs_data = data.get('faqs', [])

        # Get existing FAQs
        existing_faqs = {
            str(faq.id): faq 
            for faq in FAQ.objects.filter(
                content_type=content_type,
                object_id=object_id
            )
        }
        
        for faq_data in faqs_data:
            faq_id = faq_data.get('id')
            
            if faq_id and faq_id in existing_faqs:
                # Update existing FAQ
                faq = existing_faqs[faq_id]
                faq.question = faq_data['question']
                faq.response_type = faq_data['response_type']
                faq.answer = faq_data.get('answer', '')
                faq.save()
                
                # Handle sub-questions
                if faq.response_type == 'subquestions':
                    # Delete existing sub-questions
                    faq.sub_questions.all().delete()
                    
                    # Create new sub-questions
                    for i, sub_q in enumerate(faq_data.get('sub_questions', [])):
                        FAQSubQuestion.objects.create(
                            faq=faq,
                            question=sub_q['question'],
                            answer=sub_q['answer'],
                            order=i
                        )
            else:
                # Create new FAQ
                faq = FAQ.objects.create(
                    content_type=content_type,
                    object_id=object_id,
                    question=faq_data['question'],
                    response_type=faq_data['response_type'],
                    answer=faq_data.get('answer', '')
                )
                
                # Create sub-questions if needed
                if faq.response_type == 'subquestions':
                    for i, sub_q in enumerate(faq_data.get('sub_questions', [])):
                        FAQSubQuestion.objects.create(
                            faq=faq,
                            question=sub_q['question'],
                            answer=sub_q['answer'],
                            order=i
                        )

        return JsonResponse({'status': 'success'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
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
