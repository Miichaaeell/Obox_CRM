from django.urls import path

from students.views import (
    FrequenceStudentView,
    MonthlyFeePaymentDetailAPIView,
    MonthlyFeePaymentUpdateAPIView,
    PaymentListCreateAPIView,
    StatusStudentCreateView,
    StatusStudentListView,
    StatusStudentUpdateView,
    StudentCreateView,
    StudentDetailView,
    StudentRetriveUpdateDestroyAPIView,
    StudentListView,
    UploadFileView,
    StudentInactivationAPIView

)


urlpatterns = [

    # URLS STUDENTS
    path('', StudentListView.as_view(), name='list_student'),
    path('create_student/', StudentCreateView.as_view(), name='create_student'),
    path('detail_student/<int:pk>/',
         StudentDetailView.as_view(), name='detail_student'),
    path('api/v1/<int:pk>/',
         StudentRetriveUpdateDestroyAPIView.as_view(), name='student_api'),
    path('api/student/inactivate/', StudentInactivationAPIView.as_view(),
         name='student_inactivate_api'),

    # Urls satus
    path('status', StatusStudentListView.as_view(), name='list_status'),
    path('create_status/', StatusStudentCreateView.as_view(), name='create_status'),
    path('update_status/<int:pk>/',
         StatusStudentUpdateView.as_view(), name='update_status'),

    # Urls monthlyfee
    path("monthlyfee_update_api/<int:pk>", MonthlyFeePaymentUpdateAPIView.as_view(),
         name="monthlyfee_update_api"),
    path("api/monthlyfee/<int:pk>/", MonthlyFeePaymentDetailAPIView.as_view(),
         name="monthlyfee_detail_api"),

    # Urls frequence
    path('frequence/', FrequenceStudentView.as_view(), name='frequence'),

    # Urls Upload
    path('uploadfile/', UploadFileView.as_view(), name='uploadfile'),

    # Urls Payment

    path('payment/api/v1/', PaymentListCreateAPIView.as_view(), name='payment_api')
]
