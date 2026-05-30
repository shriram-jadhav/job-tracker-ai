from rest_framework import serializers
from .models import Application, MLResult


class MLResultSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MLResult
        fields = ['fit_score', 'interview_prob', 'skill_gaps', 'shap_values', 'suggestions']


class ApplicationSerializer(serializers.ModelSerializer):
    ml_result = MLResultSerializer(read_only=True)
    fit_score = serializers.SerializerMethodField()

    class Meta:
        model  = Application
        fields = [
            'id', 'company', 'role', 'jd_text', 'jd_url',
            'status', 'salary', 'location', 'notes',
            'fit_score', 'applied_at', 'created_at', 'updated_at',
            'ml_result'
        ]
        read_only_fields = ['id', 'fit_score', 'created_at', 'updated_at']

    def get_fit_score(self, obj):
        if hasattr(obj, 'ml_result') and obj.ml_result:
            return obj.ml_result.fit_score
        return None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)