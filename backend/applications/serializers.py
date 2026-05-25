from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Application
        fields = [
            'id', 'company', 'role', 'jd_text', 'jd_url',
            'status', 'salary', 'location', 'notes',
            'fit_score', 'applied_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'fit_score', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Auto-attach logged-in user
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)