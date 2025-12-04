from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils.dateparse import parse_datetime
from .models import User, Patient, Appointment, Report
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    PatientSerializer,
    AppointmentSerializer,
    ReportSerializer,
    AvailableDoctorSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action in ['create']:
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            if not self.request.user.is_authenticated or self.request.user.role != 'ADMIN':
                raise PermissionDenied("Only admin can modify users.")
        return [permissions.IsAuthenticated()]

class AvailableDoctorsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Query params:
        - date_time=YYYY-MM-DDTHH:MM (ISO format)
        """
        date_time_str = request.query_params.get("date_time")
        if not date_time_str:
            return Response({"error": "date_time query param is required"}, status=400)

       
        date_time = parse_datetime(date_time_str)
        if not date_time:
            return Response({"error": "Invalid date_time format"}, status=400)

       
        if not (8 <= date_time.hour < 20):
            return Response({"error": "Requested time is outside of working hours (8-20)"}, status=400)

     
        all_doctors = User.objects.filter(role="DOCTOR")

       
        busy_doctors = Appointment.objects.filter(
            doctor__role="DOCTOR",
            date_time=date_time,
            status="scheduled"
        ).values_list('doctor_id', flat=True)

        
        free_doctors = all_doctors.exclude(id__in=busy_doctors)

        serializer = AvailableDoctorSerializer(free_doctors, many=True)
        return Response(serializer.data)


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        
        serializer.save()

