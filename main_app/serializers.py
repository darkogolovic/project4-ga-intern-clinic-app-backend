from rest_framework import serializers
from .models import User, Patient, Appointment, Report
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer




class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "specialization"]
        read_only_fields = ["id", "email"]

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data

class UserCreateSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "specialization", "password"]

    def validate_role(self, value):
        
        if value not in ["ADMIN", "DOCTOR", "NURSE"]:
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class AvailableDoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'specialization']




class PatientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name", "last_name",
            "date_of_birth",
            "gender",
            "phone",
            "address",
            "medical_history",
            "doctor",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]




class AppointmentSerializer(serializers.ModelSerializer):
    doctor_id = serializers.IntegerField(write_only=True)
    nurse_id = serializers.IntegerField(write_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    report_id = serializers.IntegerField(source="report.id", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor", "nurse", "patient",
            "doctor_id", "nurse_id", "patient_id",
            "date_time",
            "status",
            "report_id"
            

        ]
        read_only_fields = ["id", "doctor", "nurse", "patient","report_id"]

    def get_has_report(self, obj):
        return hasattr(obj, "report")

    def validate(self, attrs):
        doctor_id = attrs.get('doctor_id')
        date_time = attrs.get('date_time')

       
        if not (8 <= date_time.hour < 20):
            raise serializers.ValidationError("Appointment must be between 08:00 and 20:00.")

       
        if Appointment.objects.filter(
            doctor_id=doctor_id,
            date_time=date_time,
            status="scheduled"
        ).exists():
            raise serializers.ValidationError("Doctor already has an appointment at this time.")

        return attrs

    def create(self, validated_data):
        doctor = User.objects.get(id=validated_data.pop("doctor_id"))
        nurse = User.objects.get(id=validated_data.pop("nurse_id"))
        patient = Patient.objects.get(id=validated_data.pop("patient_id"))

        appointment = Appointment.objects.create(
            doctor=doctor,
            nurse=nurse,
            patient=patient,
            **validated_data
        )
        return appointment




class ReportSerializer(serializers.ModelSerializer):
    appointment_id = serializers.IntegerField(write_only=True)
    nurse_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Report
        fields = [
            "id",
            "appointment_id",
            "diagnosis",
            "nurse_id",
            "doctor",
            "nurse",
            "patient",
            "created_at",
        ]
        read_only_fields = ["id", "doctor", "patient", "nurse","created_at"]

    def validate_appointment_id(self, value):
     
        try:
            appointment = Appointment.objects.get(id=value)
        except Appointment.DoesNotExist:
            raise serializers.ValidationError("Appointment does not exist.")

        request_user = self.context["request"].user

        if request_user.role != "DOCTOR":
            raise serializers.ValidationError("Only doctors can create reports.")

        
        if appointment.doctor != request_user:
            raise serializers.ValidationError("You can only write reports for your own appointments.")

       
        if hasattr(appointment, "report"):
            raise serializers.ValidationError("This appointment already has a report.")

        return value

    def create(self, validated_data):
        appointment = Appointment.objects.get(id=validated_data.pop("appointment_id"))

        nurse_id = validated_data.pop("nurse_id", None)
        nurse = None
        if nurse_id:
            nurse = User.objects.get(id=nurse_id, role="NURSE")

        report = Report.objects.create(
            appointment=appointment,
            doctor=self.context["request"].user,
            patient=appointment.patient,
            nurse=nurse,
            **validated_data
        )
        appointment.status = Appointment.Status.COMPLETED  
        appointment.save(update_fields=["status"])

        return report
