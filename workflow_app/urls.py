from django.urls import path
from workflow_app.views import *

urlpatterns = [
    path('', login_page, name='login_page'),
    path('manager/dashboard/',manager_dashboard,name='manager_dashboard'),
    path('logout/all/', logout_all,name='logout_all'),
    #Staff
    path('add/staff/',add_staff,name='add_staff'),
    path('view/staffs/',view_staffs,name='view_staffs'),
    path('update/staff/<id>/',update_staff,name='update_staff'),
    path('remove/staff/<id>/',remove_staff,name='remove_staff'),
    path('profile/staff/',profile_staff, name='profile_staff'),
    #Task
    path('add/task/',add_task,name='add_task'),
    path('view/tasks/',view_tasks,name='view_tasks'),
    path('update/task/<id>/',update_task,name='update_task'),
    path('remove/task/<id>/',remove_task,name='remove_task'),
    #task_selection_by_staff
    path('staff/select/task/<id>/',select_task_staff,name='select_task_staff'),
    path('staff/remove/task/<id>/',remove_task_staff,name='remove_task_staff'),
    #task completion 
    path('mark_completed/<id>/', mark_completed, name='mark_completed'),
    #task review
    path('manager/reviewed/<id>/',mark_task_completed,name='mark_task_completed'),
    #organizational Dashboard
    path('all/organizational_dashboard/',organizational_dashboard,name='organizational_dashboard'),
    #leads
    path('leads',leads,name='leads'),
    path('lead/add/',add_lead,name='add_lead'),
    path('lead/update/<id>/',update_lead,name='update_lead'),
    path('lead/remove/<id>/',remove_lead,name='remove_lead')
]
