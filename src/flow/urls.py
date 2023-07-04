from django.urls import path
from . import views

app_name = 'production'

urlpatterns = [
    path('mail', views.mail, name='mail'),
    path('send_email', views.send_email, name='send_email'),

    path('', views.index, name='index'),

    # Start Status
    path('api_project_status', views.ListProjectStatusView.as_view({'get': 'list'}), name='api_project_status'),
    # End Status

    # Start Status
    path('api_status_preset', views.ListStatusPresetView.as_view({'get': 'list'}), name='api_status_preset'),
    path('api_create_status_preset', views.api_create_status_preset, name="api_create_status_preset"),
    path('api_update_status_preset', views.api_update_status_preset, name="api_update_status_preset"),
    path('api_select_status_preset', views.api_select_status_preset, name="api_select_status_preset"),

    path('api_status_list', views.ListStatusListView.as_view({'get': 'list'}), name='api_status_list'),
    path('api_create_status_list', views.api_create_status_list, name="api_create_status_list"),
    path('api_update_status_list', views.api_update_status_list, name="api_update_status_list"),

    path('api_status', views.ListStatusView.as_view({'get': 'list'}), name='api_status'),
    path('api_add_status', views.api_add_status, name="api_add_status"),
    path('api_update_status', views.api_update_status, name="api_update_status"),
    # End Status

    # Start Company
    path('company', views.company, name="company"),
    path('renew_company/<int:company_id>/<str:company_name>', views.renew_company, name="renew_company"),
    path('api_company', views.ListCompanyView.as_view({'get': 'list'}), name='api_company'),
    path('api_create_company', views.api_create_company, name="api_create_company"),
    path('api_update_company', views.api_update_company, name="api_update_company"),
    path('api_renew_company/<int:company_id>', views.api_renew_company, name="api_renew_company"),
    path('api_invite_in_company', views.api_invite_in_company, name="api_invite_in_company"),
    path('invite/<int:company_id>', views.api_add_invited_in_company, name="invite"),

    path('api_skip_renew', views.api_skip_renew, name="api_skip_renew"),
    #  End Company

    # Start Employee
    path('api_employee', views.ListEmployeeView.as_view({'get': 'list'}), name='api_employee'),
    path('api_delete_employee', views.api_delete_employee, name="api_delete_employee"),
    path('api_employee_task_folder', views.ListEmployeeTaskFolderView.as_view({'get': 'list'}), name='api_employee_task_folder'),
    path('api_employee_task', views.ListEmployeeTaskView.as_view({'get': 'list'}), name='api_employee_task'),
    # End Employee

    # Start Project
    path('api_project_folder', views.ListProjectFolderView.as_view({'get': 'list'}), name='api_project_folder'),
    path('api_create_project_folder', views.api_create_project_folder, name="api_create_project_folder"),
    path('api_update_project_folder', views.api_update_project_folder, name="api_update_project_folder"),
    path('api_delete_project_folder', views.api_delete_project_folder, name="api_delete_project_folder"),

    path('api_project', views.ListProjectView.as_view({'get': 'list'}), name='api_project'),
    path('api_create_project', views.api_create_project, name="api_create_project"),
    path('api_update_project', views.api_update_project, name="api_update_project"),
    path('api_delete_project', views.api_delete_project, name="api_delete_project"),
    # End Project

    # Start Task
    path('api_task_head', views.ListTaskHeadView.as_view({'get': 'list'}), name='api_task_head'),
    path('api_update_task_head', views.api_update_task_head, name="api_update_task_head"),

    path('api_task_folder', views.ListTaskFolderView.as_view({'get': 'list'}), name='api_task_folder'),
    path('api_create_task_folder', views.api_create_task_folder, name="api_create_task_folder"),
    path('api_update_task_folder', views.api_update_task_folder, name="api_update_task_folder"),
    path('api_delete_task_folder', views.api_delete_task_folder, name="api_delete_task_folder"),

    path('api_task_folder_bulk_email', views.ListTaskFolderBulkEmailView.as_view({'get': 'list'}), name='api_task_folder_bulk_email'),

    path('api_task', views.ListTaskView.as_view({'get': 'list'}), name='api_task'),
    path('api_create_task', views.api_create_task, name="api_create_task"),
    path('api_update_task', views.api_update_task, name="api_update_task"),
    path('api_delete_task', views.api_delete_task, name="api_delete_task"),
    path('api_bulk_task', views.api_bulk_task, name="api_bulk_task"),
    path('api_create_task_by_site', views.api_create_task_by_site, name="api_create_task_by_site"),
    path('api_task_detail', views.ListTaskDetailView.as_view({'get': 'list'}), name='api_task_detail'),
    path('api_create_task_comment', views.api_create_task_comment, name='api_create_task_comment'),

    # End Task

    # Start Video Version
    # path('api_video_version', views.ListVideoVersionView.as_view({'get': 'list'}), name='api_video_version'),
    path('api_upload_video', views.api_upload_video, name='api_upload_video'),
    path('api_create_video_thumbnail', views.api_create_video_thumbnail, name='api_create_video_thumbnail'),
    path('api_video_comment', views.ListVideoCommentView.as_view({'get': 'list'}), name='api_video_comment'),
    path('api_create_video_comment', views.api_create_video_comment, name='api_create_video_comment'),
    path('api_update_video_comment', views.api_update_video_comment, name='api_update_video_comment'),
    # End Video Version

    # Start Sorting
    path('api_update_sorting', views.api_update_sorting, name="api_update_sorting"),
    # End Sorting

    # Start Calendar
    # path('api_calendar', views.ListCalendarView.as_view({'get': 'list'}), name='api_calendar'),
    path('api_project_calendar', views.ListProjectCalendarView.as_view({'get': 'list'}), name='api_project_calendar'),
    path('api_employee_calendar', views.ListEmployeeCalendarView.as_view({'get': 'list'}), name='api_employee_calendar'),
    path('api_update_calendar', views.api_update_calendar, name="api_update_calendar"),
    path('api_update_calendar_events', views.api_update_calendar_events, name="api_update_calendar_events"),
    path('api_delete_calendar', views.api_delete_calendar, name="api_delete_calendar"),
    # End Calendar

    # Start User Notes

    path('api_user_account', views.ListUserAccountView.as_view({'get': 'list'}), name='api_user_account'),
    path('api_user_account_key', views.api_user_account_key, name='api_user_account_key'),
    path('api_update_user_account', views.api_update_user_account, name="api_update_user_account"),
    path('api_create_user_review', views.api_create_user_review, name='api_create_user_review'),
    # End  User Account

    # Start Payment
    path('checkout', views.checkout, name="checkout"),
    path('api_checkout', views.api_checkout, name="api_checkout"),
    path('api_renew_checkout/<int:company_id>', views.api_renew_checkout, name="api_renew_checkout"),
    # End Payment

    # Start Select
    path('api_select', views.api_select, name="api_select"),
    path('api_show_tab', views.api_show_tab, name="api_show_tab"),
    # End Select

    # Start CSV Truecolor
    path('api_create_imported_task', views.api_create_imported_task, name="api_create_imported_task"),
    path('api_create_folder_tasks', views.api_create_folder_tasks, name="api_create_folder_tasks"),
    path('api_export_csv', views.api_export_csv, name="api_export_csv"),
    path('api_export_csv', views.api_export_csv, name="api_export_csv"),
    path('api_create_imported_task', views.api_create_imported_task, name="api_create_imported_task"),
    # End CSV Truecolor


    path('api_update', views.api_update, name="api_update"),
]