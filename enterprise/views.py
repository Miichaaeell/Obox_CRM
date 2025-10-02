import json
from datetime import datetime, timedelta

from django.shortcuts import render,  get_object_or_404, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy

from django.views.generic import View, CreateView, ListView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.db.models import Q, Sum
from django.utils.safestring import mark_safe

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from students.models import MonthlyFee, Student
from .models import PaymentMethod, Plan, Bill,  StatusBill
from .forms import PaymentMethodForm, PlanForm
from .serializers import BillSerializer, NFESerializer


class MonthlyFeeUpdateView(View):
    def post(self, request, *args, **kwargs):
        import json
        data = json.loads(request.body)
        if not data.get('payment_method'):
            return JsonResponse({"success": False, "message": 'Não foi selecionado nenhum metodo de pagamento'}, status=400)
        fee = get_object_or_404(MonthlyFee, pk=data.get("monthlyfee_id"))
        if fee:
            try:
                method = PaymentMethod.objects.get(
                    pk=data.get('payment_method'))
                fee.payment_method = str(method.method).upper()
                fee.paid = True
                fee.date_paid = datetime.now()
                fee.save()
            except Exception as e:
                print(f'Erro ao atualizar mensalidade -> {e}')
                return JsonResponse({"success": False, "message": 'Erro ao atualizar mensalidade'}, status=400)
            return JsonResponse({"success": True})


# Endpoint para pegar os dados de uma mensalidade


class MonthlyFeeDetailAPI(View):
    def get(self, request, pk):
        fee = get_object_or_404(MonthlyFee, pk=pk)
        payments_methods = list(
            PaymentMethod.objects.all().values_list('id', 'method'))

        return JsonResponse(
            {
                "plan": str(fee.student.plan.name_plan),
                "value": str(fee.amount),
                "paymentMethods": payments_methods,
            }
        )


class EnterpriseHomeView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        today = datetime.now()
        actives_students = Student.objects.filter(
            status__status__iexact='Ativo')
        end_date = today+timedelta(days=10)
        monthly_fees_due = MonthlyFee.objects.filter(
            due_date__range=(today, end_date), paid=False)
        date_start = today - timedelta(days=10)
        date_end = today - timedelta(days=1)
        monthly_fees_overdue = MonthlyFee.objects.filter(
            due_date__range=(date_start, date_end), paid=False)
        context = {
            'actives_total': actives_students.count(),
            'actives_students': actives_students,
            'monthly_fees_due_total': monthly_fees_due.count(),
            'monthly_fees_due': monthly_fees_due,
            'monthly_fees_overdue_total': monthly_fees_overdue.count(),
            'monthly_fees_overdue': monthly_fees_overdue,
            'today': today,
            'payment_methods': mark_safe(json.dumps(list(PaymentMethod.objects.values("id", "method")))),
        }
        return render(request, 'home.html', context)


class FlowCashierView(LoginRequiredMixin, TemplateView):
    template_name = 'flow_cashier.html'


class EnterpriseCashierView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        month, year = datetime.today().month,  datetime.today().year
        start = f'{year}-{month}-01'
        end = f'{year}-{month}-30'
        monthlyfees = MonthlyFee.objects.filter(due_date__range=(start, end))
        total = monthlyfees.aggregate(
            pix=Sum('amount', filter=Q(payment_method__iexact="pix")),
            credito=Sum('amount', filter=Q(payment_method__iexact="crédito")),
            debito=Sum('amount', filter=Q(payment_method__iexact="débito")),
            dinheiro=Sum('amount', filter=Q(
                payment_method__iexact="dinheiro")),
            tot=Sum('amount')
        )
        bill = Bill.objects.filter(due_date__range=(start, end))
        pay = bill.filter(status__status__iexact='pago').aggregate(
            total_pay=Sum('value'))
        print(pay)
        context = {
            'pix': total['pix'] if total['pix'] else 0,
            'credito': total['credito'] if total['credito'] else 0,
            'debito': total['debito'] if total['debito'] else 0,
            'dinheiro': total['dinheiro'] if total['dinheiro'] else 0,
            'tot': total['tot'] if total['tot'] else 0,
            'bills': bill if bill else 0,
            'pay': pay['total_pay'] if pay['total_pay'] else 0,
            'monthlyfees': monthlyfees,
        }
        return render(request, 'cashier.html', context)


class PaymentMethodListView(LoginRequiredMixin, ListView):
    model = PaymentMethod
    template_name = 'components/_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Métodos de Pagamento'
        context['sufix_url'] = 'payment_method'
        return context


class PaymentMethodCreateView(LoginRequiredMixin, CreateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'components/_create_update.html'
    success_url = reverse_lazy('list_payment_method')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Método de Pagamento'
        context['sufix_url'] = 'payment_method'
        return context


class PaymentMethodUpdateView(LoginRequiredMixin, UpdateView):
    model = PaymentMethod
    form_class = PaymentMethodForm
    template_name = 'components/_create_update.html'
    success_url = reverse_lazy('list_payment_method')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Método de Pagamento'
        context['sufix_url'] = 'payment_method'
        return context


class PlanListView(LoginRequiredMixin, ListView):
    model = Plan
    template_name = 'components/_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Planos'
        context['sufix_url'] = 'plan'
        return context


class PlanCreateView(LoginRequiredMixin, CreateView):
    model = Plan
    form_class = PlanForm
    template_name = 'components/_create_update.html'
    success_url = reverse_lazy('list_plan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Plano'
        context['sufix_url'] = 'plan'
        return context


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    model = Plan
    form_class = PlanForm
    template_name = 'components/_create_update.html'
    success_url = reverse_lazy('list_plan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Plano'
        context['sufix_url'] = 'plan'
        return context

    # Views for Bill


class BillListView(LoginRequiredMixin, ListView):
    model = Bill
    template_name = 'list_bill.html'
    # paginate_by = 8

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_bill'] = StatusBill.objects.all()
        context['payment_methods'] = PaymentMethod.objects.all()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('search')
        if status_filter:
            queryset = queryset.filter(status__status__icontains=status_filter)
        return queryset

# Views NFE's


class NFESListView(LoginRequiredMixin, TemplateView):
    template_name = 'nfes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        monthlyfees = MonthlyFee.objects.select_related('student', 'plan')
        context['monthlyfees'] = monthlyfees
        reference_months = (
            MonthlyFee.objects.order_by('-reference_month')
            .values_list('reference_month', flat=True)
            .distinct()
        )
        context['reference_months'] = list(reference_months)
        return context


# API'S VIEW
class BillDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer


class BillCreateAPIView(generics.ListCreateAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer


class NFEAPIView(APIView):
    def post(self, request, *args, **kwargs):

        serializer = NFESerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            students = data['student']
            description = data['description']
            reference_month = data['reference_month']

            #Criar função para rodar em segundo plano e emitir a nota
            for student in students:
                print(
                    f'emitindo nota para {student['id']}, descrição {description},mes de referencia {reference_month} ')

            return Response({
                'status': 'ok',
                'mensagem': f'{len(students)} notas agendadas para emissão.'
            },
                status=status.HTTP_202_ACCEPTED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
