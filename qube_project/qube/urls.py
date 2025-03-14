from django.urls import path
from .views import (
    main_view, register_view, login_view, logout_view,
    dashboard_view, group_view, dashboard_view, create_group_view, settings_view, group_detail_view
)

urlpatterns = [
    path('', main_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('group/', group_view, name='group'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('create-group/', create_group_view, name='create_group'),
    path('settings/', settings_view, name='settings'),
    path('group/<str:uid>/', group_detail_view, name='group_detail'),
]
