from django.urls import path
from .views import EnterpriseHomeView, PaymentMethodListView, PaymentMethodCreateView, PaymentMethodUpdateView, PlanListView, PlanCreateView, PlanUpdateView, BillListView, BillCreateAPIView, BillDetailAPIView, EnterpriseCashierView, MonthlyFeeUpdateView, MonthlyFeeDetailAPI, FlowCashierView, NFESListView

urlpatterns = [
    path('', EnterpriseHomeView.as_view(), name='home'),

    # Views Payment

    path('payment_list/', PaymentMethodListView.as_view(),
         name='list_payment_method'),
    path('payment_create/', PaymentMethodCreateView.as_view(),
         name='create_payment_method'),
    path('payment_update/<int:pk>/', PaymentMethodUpdateView.as_view(),
         name='update_payment_method'),

    # Views Plan
    path('plan_list/', PlanListView.as_view(), name='list_plan'),
    path('plan_create/', PlanCreateView.as_view(), name='create_plan'),
    path('plan_update/<int:pk>/', PlanUpdateView.as_view(), name='update_plan'),

    # Views Bill
    path('bill_list/', BillListView.as_view(), name='list_bill'),
    path('bill/api/v1/', BillCreateAPIView.as_view(), name='create_bill'),
    path('bill/api/v1/<int:pk>/',
         BillDetailAPIView.as_view(), name='detail_bill'),
    # Views Cashier
    path('cashier/', EnterpriseCashierView.as_view(), name='cashier'),

    # Views Monthyfee
    path("monthlyfee_update_api/", MonthlyFeeUpdateView.as_view(),
         name="monthlyfee_update_api"),
    path("api/monthlyfee/<int:pk>/", MonthlyFeeDetailAPI.as_view(),
         name="monthlyfee_detail_api"),
    path('flow_cashier/', FlowCashierView.as_view(), name='flow_cashier'),
    
     #Views NFE's
     path('nfes', NFESListView.as_view(), name='nfes')
]
