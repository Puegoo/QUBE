from django.urls import path
from .views import (
    main_view, register_view, login_view, logout_view,
    dashboard_view, group_view, create_group_view, settings_view, 
    group_detail_view, add_task_view, add_member_view, edit_task_view, edit_member_view, update_group_name_view, delete_group_view
)

urlpatterns = [
    path('', main_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('group/', group_view, name='group'),
    path('create-group/', create_group_view, name='create_group'),
    path('settings/', settings_view, name='settings'),
    path('group/<str:group_uid>/', group_detail_view, name='group_detail'),
    path('group/<str:group_uid>/add-task/', add_task_view, name='add_task'),
    path('group/<str:group_uid>/add-member/', add_member_view, name='add_member'),
    path('group/<str:group_uid>/edit_task/<str:task_uid>/', edit_task_view, name='edit_task'),
    path('group/<str:group_uid>/edit_member/<str:username>/', edit_member_view, name='edit_member'),
    path('group/<str:uid>/update-name/', update_group_name_view, name='update_group_name'),
    path('group/<str:group_uid>/delete/', delete_group_view, name='delete_group'),
]