from rest import serializers
from .models import User, Patient, Appointment, Report




class UserSerializer(serializers.ModelSerializer):
    """Basic serializer for doctors, nurses, and admin users."""
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "specialization"]
        read_only_fields = ["id", "email"]


class UserCreateSerializer(serializers.ModelSerializer):
    """Used by app-admin in React UI to create new doctors / nurses / admin users."""
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "specialization", "password"]

    def validate_role(self, value):
        """App admin can create only DOCTOR or NURSE or ADMIN — no Superuser."""
        if value not in ["ADMIN", "DOCTOR", "NURSE"]:
            raise serializers.ValidationError("Invalid role.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user




class PatientSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "first_name", "last_name",
            "date_of_birth",
            "gender",
            "phone_number",
            "address",
            "medical_history",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]




class AppointmentSerializer(serializers.ModelSerializer):
    doctor = UserSerializer(read_only=True)
    nurse = UserSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)

    doctor_id = serializers.IntegerField(write_only=True)
    nurse_id = serializers.IntegerField(write_only=True)
    patient_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "doctor", "nurse", "patient",
            "doctor_id", "nurse_id", "patient_id",
            "date",
            "start_time",
            "end_time",
            "notes",
        ]
        read_only_fields = ["id"]

    def validate_doctor_id(self, value):
        user = User.objects.get(id=value)
        if user.role != "DOCTOR":
            raise serializers.ValidationError("Selected user is not a doctor.")
        return value

    def validate_nurse_id(self, value):
        user = User.objects.get(id=value)
        if user.role != "NURSE":
            raise serializers.ValidationError("Selected user is not a nurse.")
        return value

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
    appointment = AppointmentSerializer(read_only=True)
    appointment_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Report
        fields = ["id", "appointment", "appointment_id", "description", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_appointment_id(self, value):
        app = Appointment.objects.get(id=value)
        if self.context["request"].user.role != "DOCTOR":
            raise serializers.ValidationError("Only doctors can write reports.")
        return value

    def create(self, validated_data):
        appointment = Appointment.objects.get(id=validated_data.pop("appointment_id"))
        report = Report.objects.create(
            appointment=appointment,
            **validated_data
        )
        return report
