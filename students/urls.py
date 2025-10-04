from django.urls import path

from students.views import (
    FrequenceStudentView,
    MonthlyFeePaymentDetailAPIView,
    MonthlyFeePaymentUpdateAPIView,
    StatusStudentCreateView,
    StatusStudentListView,
    StatusStudentUpdateView,
    StudentCreateView,
    StudentDetailView,
    StudentDestroyAPIView,
    StudentListView,
    StudentUpdateView,
    UploadFileView,
    StudentInactivationAPIView
)


urlpatterns = [

    # URLS STUDENTS
    path('', StudentListView.as_view(), name='list_student'),
    path('create_student/', StudentCreateView.as_view(), name='create_student'),
    path('update_student/<int:pk>/',
         StudentUpdateView.as_view(), name='update_student'),
    path('detail_student/<int:pk>/',
         StudentDetailView.as_view(), name='detail_student'),
    path('student/delete/<int:pk>/',
         StudentDestroyAPIView.as_view(), name='student_delete_api'),
    path('api/student/inactivate/', StudentInactivationAPIView.as_view(),
         name='student_inactivate_api'),

    # Urls satus
    path('status', StatusStudentListView.as_view(), name='list_status'),
    path('create_status/', StatusStudentCreateView.as_view(), name='create_status'),
    path('update_status/<int:pk>/',
         StatusStudentUpdateView.as_view(), name='update_status'),

    # Urls monthlyfee
    path("monthlyfee_update_api/", MonthlyFeePaymentUpdateAPIView.as_view(),
         name="monthlyfee_update_api"),
    path("api/monthlyfee/<int:pk>/", MonthlyFeePaymentDetailAPIView.as_view(),
         name="monthlyfee_detail_api"),

    # Urls frequence
    path('frequence/', FrequenceStudentView.as_view(), name='frequence'),

    # Urls Upload
    path('uploadfile/', UploadFileView.as_view(), name='uploadfile')
]
