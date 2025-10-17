from django.urls import path

from enterprise.views import (
    BillCreateAPIView,
    BillDetailAPIView,
    BillListView,
    DownloadCashierFlowView,
    EnterpriseCashierView,
    EnterpriseHomeView,
    FlowCashierView,
    NFEAPIView,
    NFESListView,
    PaymentMethodCreateView,
    PaymentMethodListView,
    PaymentMethodUpdateView,
    PlanCreateView,
    PlanListView,
    PlanUpdateView,

)


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
    path('donwload_cashier/',
         DownloadCashierFlowView.as_view(), name='download_cashier'),

    # Views Cashier

    path('flow_cashier/', FlowCashierView.as_view(), name='flow_cashier'),

    # Views NFE's
    path('nfes', NFESListView.as_view(), name='nfes'),
    path('nfe_api', NFEAPIView.as_view(), name='nfe_api'),
]
