from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserViewSet,
    PatientViewSet,
    AppointmentViewSet,
    ReportViewSet,
    AvailableDoctorsView,
    MyTokenObtainPairView,
    MeView,
    AvailableDoctorSlotsView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('api/login/', MyTokenObtainPairView.as_view(), name='login'),
    path('api/me/', MeView.as_view()),
    path('api/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/available-doctors/', AvailableDoctorsView.as_view()),
    path(
        'api/appointments/available-slots/',
        AvailableDoctorSlotsView.as_view(),
        name='available-slots',
    ),
    
    path('api/', include(router.urls)),
]

