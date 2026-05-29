from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Resume
from .serializers import ResumeSerializer
from .parser import parse_resume


class ResumeUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=400)
        if not file.name.endswith('.pdf'):
            return Response({'error': 'Only PDF files are allowed'}, status=400)

        # Save file first (get a real path on disk)
        resume, _ = Resume.objects.update_or_create(
            user=request.user,
            defaults={'file': file}
        )

        # Run parser on saved file
        parsed = parse_resume(resume.file.path)

        # Save parsed data back to DB
        resume.raw_text       = parsed['raw_text']
        resume.skills         = parsed['skills']
        resume.experience_yrs = parsed['experience_yrs']
        resume.education      = parsed['education']
        resume.certifications = parsed['certifications']
        resume.save()

        return Response(ResumeSerializer(resume).data, status=200)

    def get(self, request):
        try:
            resume = Resume.objects.get(user=request.user)
            return Response(ResumeSerializer(resume).data)
        except Resume.DoesNotExist:
            return Response({'error': 'No resume uploaded yet'}, status=404)