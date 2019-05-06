from django.urls import path, include
from django.conf.urls import url
from . import views
# from rest_framework import routers
from rest_framework_jwt.views import refresh_jwt_token

# router = routers.DefaultRouter()
# router.register(r'enrollments', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

urlpatterns = [
    # path('api/backend/', views.BackendListCreate.as_view() ),
    path('api/enrollments/', views.EnrollmentList.as_view() ),
    path('api/parents/', views.ParentList.as_view() ),
    path('api/children/', views.ChildList.as_view() ),
    path('api/activities/', views.ActivityList.as_view() ),
    path('api/activity/<int:pk>/', views.ActivityRUDView.as_view() ),
    path('api/make_activity/', views.activity_post ),
    path('api/rud_enrollment/<int:pk>/', views.EnrollmentRUD.as_view() ),
    path('api/batch_update_enrollments/', views.batch_update_enrollments),
    path('api/confirm_enrollment/<int:pk>/', views.confirm_enrollment),
    path('api/cancel_enrollment/<int:pk>/', views.cancel_enrollment),
    path('api/create_enrollment/', views.create_enrollment ),
    path('api/resend_confirm/<int:pk>/', views.resend_confirm), 
    path('api/send_weekly_update/', views.send_all_emails),
    path('api/enrollments_by_token/<str:token>/', views.enrollments_by_token), 
    path('api/login/', views.LoginView.as_view()),
    path('api/registration/', views.RegisterUsers.as_view()),
    url(r'^rest-auth/', include('rest_auth.urls')), #rest-auth/login/, rest-auth/logout/
    url(r'^rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^refresh-token/', refresh_jwt_token)
    # path('api/sendemail/', views.send_email())
]