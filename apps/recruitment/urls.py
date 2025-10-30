from django.urls import path
from .views import recruitment_home, recruitment_candidates, recruitment_applications, recruitment_interviews,recruitment_statistics,recruitment_pointage,recruitment_suivi,recruitment_interview_kanban_stage,get_interview_json,export_candidates_excel,export_candidates_pdf,interview_events_json,recruitment_interview_set_result,recruitment_archived_interviews,department_distribution_api,employee_pointages,recruitment_evaluation,cv_upload_parse,save_parsed_candidates
from . import views

urlpatterns = [
    path('', recruitment_home, name='recruitment_home'),
    path('candidates/', recruitment_candidates, name='recruitment_candidates'),
    path('applications/', recruitment_applications, name='recruitment_applications'),
    path('interviews/', recruitment_interviews, name='recruitment_interviews'),
    path('statistics/', recruitment_statistics, name='recruitment_statistics'),
    path('pointage/', recruitment_pointage, name='recruitment_pointage'),
    path('suivi/', recruitment_suivi, name='recruitment_suivi'),
    path('evaluation/', recruitment_evaluation, name='recruitment_evaluation'),
    path('evaluation/pdf/<int:evaluation_id>/', views.download_evaluation_pdf, name='download_evaluation_pdf'),
    path('employee/<int:employee_id>/pointages/', employee_pointages, name='employee_pointages'),
    path('interviews/json/<int:interview_id>/', get_interview_json, name='get_interview_json'),
    
    path('interview/kanban_stage/', recruitment_interview_kanban_stage, name='recruitment_interview_kanban_stage'),
    path('interview/<int:interview_id>/json/', views.get_interview_json, name='recruitment_interview_json'),
    path('candidates/export/excel/', export_candidates_excel, name='export_candidates_excel'),
    path('candidates/export/pdf/', export_candidates_pdf, name='export_candidates_pdf'),
    path('interview/events/', interview_events_json, name='interview_events_json'),
    path('interview/set_result/', recruitment_interview_set_result, name='recruitment_interview_set_result'),
    path('interview/archived/', recruitment_archived_interviews, name='recruitment_archived_interviews'),
    path('api/department-distribution/', department_distribution_api, name='department_distribution_api'),


    # CV Upload and Parsing URLs
    path('cv/upload-parse/', cv_upload_parse, name='cv_upload_parse'),
    path('cv/save-candidates/', save_parsed_candidates, name='save_parsed_candidates'),
]
