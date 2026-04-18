from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('support/', views.support, name='support'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('timetables/', views.timetable_list, name='timetable_list'),
    path('courses/', views.course_list, name='course_list'),
    path('instructors/', views.instructor_list, name='instructor_list'),
    path('send-timetable/', views.send_timetable_email, name='send_timetable'),
]
