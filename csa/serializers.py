from rest_framework import serializers
from .models import CSA, FAQ, SubQuestion

class SubQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubQuestion
        fields = ['id', 'question', 'answer']

class FAQSerializer(serializers.ModelSerializer):
    sub_questions = SubQuestionSerializer(many=True, required=False)
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'response_type', 'answer', 'sub_questions']

class CSASerializer(serializers.ModelSerializer):
    faqs = serializers.ListField(write_only=True, required=False)
    
    class Meta:
        model = CSA
        fields = ['id', 'name', 'description', 'firebase_path', 'faqs']
        read_only_fields = ['firebase_path']

    def validate_faqs(self, value):
        """Validate FAQ data structure"""
        if not value:
            return value
            
        valid_response_types = ['answer', 'subquestions']
        
        for faq in value:
            # Check required fields
            if 'question' not in faq:
                raise serializers.ValidationError("Each FAQ must have a question")
            if 'response_type' not in faq:
                raise serializers.ValidationError("Each FAQ must have a response_type")
            
            # Validate response_type
            if faq['response_type'] not in valid_response_types:
                raise serializers.ValidationError(
                    f"Invalid response_type. Must be one of: {valid_response_types}"
                )
            
            # Validate based on response_type
            if faq['response_type'] == 'answer':
                if 'answer' not in faq:
                    raise serializers.ValidationError("FAQ with response_type 'answer' must have an answer")
            elif faq['response_type'] == 'subquestions':
                if 'sub_questions' not in faq:
                    raise serializers.ValidationError("FAQ with response_type 'subquestions' must have sub_questions")
                if not isinstance(faq['sub_questions'], list):
                    raise serializers.ValidationError("sub_questions must be a list")
                for sub_q in faq['sub_questions']:
                    if 'question' not in sub_q or 'answer' not in sub_q:
                        raise serializers.ValidationError("Each sub-question must have both question and answer")
        
        return value

    def create(self, validated_data):
        # Remove faqs from validated_data as it's not a model field
        faqs = validated_data.pop('faqs', [])
        
        # Create CSA instance
        csa = super().create(validated_data)
        
        # Store faqs in the instance for the view to use
        csa._faqs = faqs
        return csa
