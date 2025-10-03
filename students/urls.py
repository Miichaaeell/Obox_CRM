from django.urls import path

from students.views import (
    FrequenceStudentView,
    MonthlyFeeDeleteView,
    MonthlyFeeUpdateView,
    StatusStudentCreateView,
    StatusStudentListView,
    StatusStudentUpdateView,
    StudentCreateView,
    StudentDetailView,
    StudentListView,
    StudentUpdateView,
    UploadFileView,
)


urlpatterns = [
    path('', StudentListView.as_view(), name='list_student'),
    path('create_student/', StudentCreateView.as_view(), name='create_student'),
    path('update_student/<int:pk>/',
         StudentUpdateView.as_view(), name='update_student'),
    path('detail_student/<int:pk>/',
         StudentDetailView.as_view(), name='detail_student'),
    path('status', StatusStudentListView.as_view(), name='list_status'),
    path('create_status/', StatusStudentCreateView.as_view(), name='create_status'),
    path('update_status/<int:pk>/',
         StatusStudentUpdateView.as_view(), name='update_status'),

    path('monthlyfee_update/',
         MonthlyFeeUpdateView.as_view(), name='monthlyfee_update'),
    path('monthlyfee_delete/',
         MonthlyFeeDeleteView.as_view(), name='monthlyfee_delete'),
    path('frequence/', FrequenceStudentView.as_view(), name='frequence'),
    path('uploadfile/', UploadFileView.as_view(), name='uploadfile')
]
