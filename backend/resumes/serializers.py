from rest_framework import serializers
from .models import Resume


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Resume
        fields = [
            'id', 'file', 'skills', 'experience_yrs',
            'education', 'certifications', 'uploaded_at'
        ]
        read_only_fields = [
            'id', 'skills', 'experience_yrs',
            'education', 'certifications', 'uploaded_at'
        ]