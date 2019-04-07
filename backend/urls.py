from django.urls import path
from . import views

urlpatterns = [
    # path('api/backend/', views.BackendListCreate.as_view() ),
    path('api/enrollments/', views.EnrollmentList.as_view() ),
    path('api/parents/', views.ParentList.as_view() ),
    path('api/children/', views.ChildList.as_view() ),
    path('api/activities/', views.ActivityList.as_view() ),
    path('api/make_activity/', views.activity_post ),
    # path('api/sendemail/', views.send_email())
]
