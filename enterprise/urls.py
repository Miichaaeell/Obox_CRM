from django.urls import path

from enterprise.views import (
    BillCreateAPIView,
    BillDetailAPIView,
    BillListView,
    CreateListPlanAPIView,
    DownloadCashierFlowView,
    EnterpriseCashierView,
    EnterpriseHomeView,
    EnterpriseSettingsView,
    FlowCashierView,
    NFEAPIView,
    NFESListView,
    ListCreateServiceAPIView,
    PaymentMethodCreateView,
    PaymentMethodListView,
    PaymentMethodUpdateView,
    RetriveUpdateDestroyServiceAPIView,
    RetriveUpdateDestroyPlanAPIView,
)


urlpatterns = [
    path('', EnterpriseHomeView.as_view(), name='home'),
    path('settings/', EnterpriseSettingsView.as_view(), name='settings'),

    # Views Payment

    path('payment_list/', PaymentMethodListView.as_view(),
         name='list_payment_method'),
    path('payment_create/', PaymentMethodCreateView.as_view(),
         name='create_payment_method'),
    path('payment_update/<int:pk>/', PaymentMethodUpdateView.as_view(),
         name='update_payment_method'),

    # Views Plan
    path('plan/api/v1/',CreateListPlanAPIView.as_view(), name='plan_api'),
    path('plan/api/v1/<int:pk>', RetriveUpdateDestroyPlanAPIView.as_view(), name='plan_api'),
    
    #Views Service
    path('service/api/v1/', ListCreateServiceAPIView.as_view(), name='service'),
    path('service/api/v1/<int:pk>/', RetriveUpdateDestroyServiceAPIView.as_view(), name='service'),

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
