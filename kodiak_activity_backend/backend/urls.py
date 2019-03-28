from django.urls import path
from . import views

urlpatterns = [
    path('api/backend/', views.BackendListCreate.as_view() ),
    path('api/enrollments/', views.EnrollmentList.as_view() )
]
