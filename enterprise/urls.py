from django.urls import path

from enterprise.views import (
    BillCreateAPIView,
    BillDetailAPIView,
    BillListView,
    DownloadCashierFlowView,
    EnterpriseCashierView,
    EnterpriseHomeView,
    EnterpriseSettingsView,
    FlowCashierView,
    NFEAPIView,
    NFESListView,
    ListCreateEnterpriseAPIView,
    ListCreatePaymentMethodAPIView,
    ListCreateServiceAPIView,
    ListCreatePlanAPIView,
    RetriveUpdateDestroyEnterpriseAPIView,
    RetriveUpdateDestroyPaymentMethodAPIView,
    RetriveUpdateDestroyServiceAPIView,
    RetriveUpdateDestroyPlanAPIView,
)


urlpatterns = [
     #Views Enterprise
    path('', EnterpriseHomeView.as_view(), name='home'),
    path('settings/', EnterpriseSettingsView.as_view(), name='settings'),
    path('enterprise/api/v1', ListCreateEnterpriseAPIView.as_view(), name='enterprise_api'),
    path('enterprise/api/v1/<int:pk>', RetriveUpdateDestroyEnterpriseAPIView.as_view(), name='enterprise_api'),

    # Views Payment
     path('paymentmethods/api/v1/', ListCreatePaymentMethodAPIView().as_view(), name='payment_method'),
     path('paymentmethods/api/v1/<int:pk>', RetriveUpdateDestroyPaymentMethodAPIView().as_view(), name='payment_method'),
    # Views Plan
    path('plan/api/v1/',ListCreatePlanAPIView.as_view(), name='plan_api'),
    path('plan/api/v1/<int:pk>', RetriveUpdateDestroyPlanAPIView.as_view(), name='plan_api'),
    
    #Views Service
    path('service/api/v1/', ListCreateServiceAPIView.as_view(), name='service_api'),
    path('service/api/v1/<int:pk>', RetriveUpdateDestroyServiceAPIView.as_view(), name='service_api'),

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
