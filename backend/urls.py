from django.urls import path
from . import views

urlpatterns = [
    # path('api/backend/', views.BackendListCreate.as_view() ),
    path('api/enrollments/', views.EnrollmentList.as_view() ),
    path('api/parents/', views.ParentList.as_view() ),
    path('api/children/', views.ChildList.as_view() ),
    path('api/activities/', views.ActivityList.as_view() ),
    path('api/activity/<int:pk>/', views.ActivityDetailsView.as_view() ),
    path('api/make_activity/', views.activity_post ),
    path('api/rud_enrollment/<int:pk>/', views.EnrollmentRUD.as_view() ),
    path('api/batch_update_enrollments/', views.batch_update_enrollments),
    path('api/confirm_enrollment/<int:pk>/', views.confirm_enrollment),
    path('api/cancel_enrollment/<int:pk>/', views.cancel_enrollment),
    path('api/create_enrollment/', views.create_enrollment ),
    path('api/resend_confirm/<int:pk>/', views.resend_confirm), 
    path('api/enrollments_by_token/<str:token>/', views.enrollments_by_token), 
    path('api/login/', views.login ),
    # path('api/sendemail/', views.send_email())
]