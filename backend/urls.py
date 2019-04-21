from django.urls import path
from . import views

urlpatterns = [
    # path('api/backend/', views.BackendListCreate.as_view() ),
    path('api/enrollments/', views.EnrollmentList.as_view() ),
    path('api/parents/', views.ParentList.as_view() ),
    path('api/children/', views.ChildList.as_view() ),
    path('api/activities/', views.ActivityList.as_view() ),
    path('api/make_activity/', views.activity_post ),
    path('api/rud_enrollment/<int:pk>/', views.EnrollmentRUD.as_view() ),
    path('api/confirm_enrollment/<int:pk>/', views.confirm_enrollment),
    path('api/cancel_enrollment/<int:pk>/', views.cancel_enrollment),
    path('api/create_enrollment/', views.create_enrollment ),
    path('api/sign_in/', views.sign_in ),
    # path('api/sendemail/', views.send_email())
]