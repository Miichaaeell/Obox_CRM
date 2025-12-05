import json

from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import  Q
from django.shortcuts import render
from django.urls import reverse, reverse_lazy

from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View
from django.http import JsonResponse, FileResponse

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.functions import (
    create_file_xlsx_cashier,
    create_new_register_cashier,
    get_context_cashier_data,
    get_context_homeview,
    get_dashboard_context,
    close_cashier,
)
from enterprise.models import Bill, Cashier, PaymentMethod, Plan, Service, StatusBill, Enterprise
from enterprise.serializers import (
    BillSerializer,
    NFESerializer,
    PlanSerializer,
    ServiceSerializer, 
    EnterpriseSerializer,
    PaymentMethodSerializer
)
from enterprise.tasks import send_NFS
from students.models import MonthlyFee


class EnterpriseHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = get_context_homeview()
        return render(request, 'home.html', context)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_dashboard_context())
        return context


class EnterpriseSettingsView(LoginRequiredMixin, TemplateView):
    template_name= 'settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['plans'] = Plan.objects.all().only('name_plan', 'price', 'duration_months')
        context['services'] = Service.objects.all().only('service', 'price')
        context['enterprise'] = Enterprise.objects.first()
        context['payments'] = PaymentMethod.objects.all()
        context['url_plan'] = reverse('plan_api')
        context['url_service'] = reverse('service_api')
        context['url_enterprise'] = reverse('enterprise_api')
        context['url_payments'] = reverse('payment_method')
        return context
    

class FlowCashierView(LoginRequiredMixin, TemplateView):
    template_name = 'flow_cashier.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cashiers = Cashier.objects.all().order_by('-created_at')
        context['cashiers'] = cashiers
        context['url_download'] = reverse('download_cashier')
        return context


class DownloadCashierFlowView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        cashier_id = request.GET.get("pk")
        try:
            cashier = Cashier.objects.get(id=cashier_id)
            response = create_file_xlsx_cashier(cashier)
            buffer = response[0]
            file_name = response[1]
            return FileResponse(buffer, as_attachment=True, filename=file_name, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Cashier.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Caixa não encontrado."
            }, status=404)


class EnterpriseCashierView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        context = get_context_cashier_data()
        return render(request, 'cashier.html', context)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        action = data.get('action', 'create')
        if action == 'update':
            context = get_context_cashier_data()
            withdrawalValue = int(data.get('withdrawalValue', 0))
            closing_balance = int(data.get('closing_balance', 0))
            response = close_cashier(context, withdrawalValue, closing_balance)
            return response
        elif action == 'create':
            response = create_new_register_cashier()
            return response


    # Views for Bill
class BillListView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'list_bill.html'
    # paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_bill'] = StatusBill.objects.all()
        context['payment_methods'] = PaymentMethod.objects.all()
        context['current_created_date'] = self.request.GET.get(
            'created_date', '')
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        due_date = self.request.GET.get('due_date')
        search = self.request.GET.get("search", "").strip()

        filters = Q()

        if search:
            # Tentativa 1: usuário digitou no formato dd/mm/yyyy
            try:
                parsed_date = datetime.strptime(search, "%d/%m/%Y").date()
                filters |= Q(due_date=parsed_date)
            except ValueError:
                pass

            # Tentativa 2: usuário digitou no formato yyyy-mm-dd
            try:
                parsed_date = datetime.strptime(search, "%Y-%m-%d").date()
                filters |= Q(due_date=parsed_date)
            except ValueError:
                pass
            try:
                parsed_month = datetime.strptime(search, "%m/%Y")
                filters |= Q(due_date__year=parsed_month.year,
                             due_date__month=parsed_month.month)
            except ValueError:
                pass

            try:
                parsed_month = datetime.strptime(search, "%m/%y")
                filters |= Q(due_date__year=parsed_month.year,
                             due_date__month=parsed_month.month)
            except ValueError:
                pass
            # Caso contrário, trate o search como texto (ex: nome, plano etc.)
            filters |= Q(status__status__icontains=search)

        queryset = Bill.objects.filter(filters)
        if due_date:
            try:
                parsed_date = datetime.strptime(
                    due_date, "%Y-%m-%d").date()
                queryset = queryset.filter(due_date=parsed_date)
            except ValueError:
                pass
        return queryset

# Views NFE's


class NFESListView(LoginRequiredMixin, TemplateView):
    template_name = 'nfes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        monthlyfees = MonthlyFee.objects.select_related(
            'student', 'plan').prefetch_related( 'payments').filter(paid=True)
        context['monthlyfees'] = monthlyfees
        reference_months = (
            MonthlyFee.objects.order_by('-reference_month')
            .values_list('reference_month', flat=True)
            .distinct()
        )
        context['reference_months'] = list(reference_months)
        return context


# API'S VIEW

#Views Bill
class BillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer


class BillCreateAPIView(generics.ListCreateAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer


#Views Plan
class ListCreatePlanAPIView(generics.ListCreateAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer

class RetriveUpdateDestroyPlanAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    
    
#Views Service
class ListCreateServiceAPIView(generics.ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class RetriveUpdateDestroyServiceAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    

#Views EnterpriseData
class ListCreateEnterpriseAPIView(generics.ListCreateAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    
class RetriveUpdateDestroyEnterpriseAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    
class ListCreatePaymentMethodAPIView(generics.ListCreateAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    
class RetriveUpdateDestroyPaymentMethodAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class NFEAPIView(APIView):
    def post(self, request, *args, **kwargs):

        serializer = NFESerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            response = send_NFS.delay(data)

            return Response({
                'status': 'ok',
                'mensagem': f'notas agendadas para emissão.'
            },
                status=status.HTTP_202_ACCEPTED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
