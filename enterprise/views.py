import json
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q, Sum
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.safestring import mark_safe
from django.views.generic import CreateView, ListView, TemplateView, UpdateView, View
from django.http import JsonResponse

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from enterprise.forms import PaymentMethodForm, PlanForm
from enterprise.models import Bill, PaymentMethod, Plan, StatusBill, Cashier, Installments
from enterprise.serializers import (
    BillSerializer,
    NFESerializer,
)
from students.models import MonthlyFee, Student, Payment


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
        installments = Installments.objects.all()
        bill_events = (
            Bill.objects.annotate(
                event_date=F('due_date'))
            .values('event_date')
            .annotate(count=Count('id'))
            .order_by('event_date')
        )
        calendar_events = [
            {
                "date": event.get('event_date').isoformat(),
                "count": event.get('count', 0),
            }
            for event in bill_events
            if event.get('event_date') is not None
        ]
        context = {
            'actives_total': actives_students.count(),
            'actives_students': actives_students,
            'monthly_fees_due_total': monthly_fees_due.count(),
            'monthly_fees_due': monthly_fees_due,
            'monthly_fees_overdue_total': monthly_fees_overdue.count(),
            'monthly_fees_overdue': monthly_fees_overdue,
            'today': today,
            'payment_methods':  PaymentMethod.objects.filter(
                applies_to__icontains='students'),
            'calendar_events': mark_safe(json.dumps(calendar_events)),
            'accounts_url': reverse('list_bill'),
            'students_active_url': f"{reverse('list_student')}?filter=ativo",
            'installments': installments,
        }
        return render(request, 'home.html', context)


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
        cashier_id = request.GET.get('pk')
        try:
            cashier = Cashier.objects.get(id=cashier_id)
        except Cashier.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'title': 'Erro no Download',
                'message': 'Caixa não encontrado.'
            }, status=404)
        response = JsonResponse({
            'status': 'success',
            'title': 'Download do Relatório',
            'message': f'Relatório do caixa {cashier} baixado com sucesso!'
        }, status=200)

        return response
    


class EnterpriseCashierView(LoginRequiredMixin, View):

    def _get_context_data(self):
        last_cashier = Cashier.objects.order_by('-created_at').first()
        if last_cashier.status == 'closed':
            context = {
                'status': last_cashier.get_status_display(),
                'income_pix': last_cashier.income_pix,
                'income_credit': last_cashier.income_credit,
                'income_debit': last_cashier.income_debit,
                'income_cash': last_cashier.income_cash,
                'total_incomes': last_cashier.total_incomes,
                'bills': last_cashier.bills.all(),
                'expense_pix': last_cashier.expense_pix,
                'expense_boleto': last_cashier.expense_boleto,
                'expense_automatic': last_cashier.expense_automatic,
                'expense_others': last_cashier.expense_others,
                'expense_withdrawal': last_cashier.expense_withdrawal,
                'total_expenses': last_cashier.total_expenses,
                'payments': last_cashier.payments.all(),
                'date_start': last_cashier.created_at,
                'date_end': last_cashier.date_closing,
                'opening_balance': last_cashier.opening_balance,
                'closing_balance': last_cashier.closing_balance
            }
            return context
        start = last_cashier.created_at
        end = datetime.now()
        payments = Payment.objects.filter(Q(created_at__gte=(start))
                                          | Q(created_at__lte=(end)),
                                          cashier__isnull=True)
        total = payments.aggregate(
            income_pix=Sum('value', filter=Q(payment_method__iexact="pix")),
            income_credit=Sum('value', filter=Q(
                payment_method__iexact="credito")),
            income_debit=Sum('value', filter=Q(
                payment_method__iexact="debito")),
            income_cash=Sum('value', filter=Q(
                payment_method__iexact="dinheiro")),
            total_incomes=Sum('value')
        )
        bill = Bill.objects.select_related(
            'payment_method', 'status').filter(Q(date_payment__gte=(start)) |
                                               Q(date_payment__lte=(end)), cashier__isnull=True)
        pay = bill.filter(Q(status__status__iexact='pago') | Q(payment_method__method__icontains='automatico')).aggregate(
            total_expenses=Sum('value'),
            expense_pix=Sum('value', filter=Q(
                payment_method__method__iexact='pix')),
            expense_boleto=Sum('value', filter=Q(
                payment_method__method__iexact='boleto')),
            expense_automatic=Sum('value', filter=Q(
                payment_method__method__iexact='deb. automatico')),
            expense_others=Sum('value', filter=Q(payment_method__method__iexact='credito') | Q(
                payment_method__method__iexact='debito')),
        )
        income = total['total_incomes'] or 0
        expense = pay['total_expenses'] or 0
        last_balance = Cashier.objects.filter(
            status='closed').order_by('-created_at').first()
        print(last_balance.closing_balance)
        closing_balance = last_balance.closing_balance + income - expense
        expense_withdrawal = last_cashier.expense_withdrawal
        context = {
            'status': last_cashier.get_status_display(),
            'income_pix': total['income_pix'] if total['income_pix'] else 0,
            'income_credit': total['income_credit'] if total['income_credit'] else 0,
            'income_debit': total['income_debit'] if total['income_debit'] else 0,
            'income_cash': total['income_cash'] if total['income_cash'] else 0,
            'total_incomes': total['total_incomes'] if total['total_incomes'] else 0,
            'bills': bill,
            'expense_pix': pay['expense_pix'] if pay['expense_pix'] else 0,
            'expense_boleto': pay['expense_boleto'] if pay['expense_boleto'] else 0,
            'expense_automatic': pay['expense_automatic'] if pay['expense_automatic'] else 0,
            'expense_others': pay['expense_others'] if pay['expense_others'] else 0,
            'expense_withdrawal': expense_withdrawal,
            'total_expenses': pay['total_expenses'] if pay['total_expenses'] else 0,
            'payments': payments,
            'date_start': start,
            'opening_balance': last_balance.closing_balance if last_balance else 0,
            'closing_balance': closing_balance if closing_balance else 0
        }
        return context

    def get(self, request, *args, **kwargs):
        context = self._get_context_data()
        return render(request, 'cashier.html', context)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        action = data.get('action', 'create')
        if action == 'update':
            context = self._get_context_data()
            try:
                withdrawalValue = data.get('withdrawalValue', 0)
                closing_balance = data.get('closing_balance', 0)
                last_cashier = Cashier.objects.order_by('-created_at').first()
                last_cashier.status = 'closed'
                last_cashier.date_closing = datetime.now()
                last_cashier.total_incomes = context['total_incomes']
                last_cashier.total_expenses = context['total_expenses'] + withdrawalValue
                last_cashier.closing_balance = closing_balance
                last_cashier.income_pix = context['income_pix']
                last_cashier.income_credit = context['income_credit']
                last_cashier.income_debit = context['income_debit']
                last_cashier.income_cash = context['income_cash']
                last_cashier.expense_pix = context['expense_pix']
                last_cashier.expense_boleto = context['expense_boleto']
                last_cashier.expense_automatic = context['expense_automatic']
                last_cashier.expense_others = context['expense_others']
                last_cashier.expense_withdrawal = withdrawalValue
                last_cashier.save()
                # Atualizar os pagamentos e contas vinculando ao caixa fechado
                context['bills'].update(cashier=last_cashier)
                context['payments'].update(cashier=last_cashier)
                return JsonResponse({'status': 'success', 'title': 'Fechamento do Caixa', 'message': f'Caixa fechado com sucesso! Saldo final R${closing_balance}, Retirado: R${withdrawalValue}'}, status=200)
            except Exception as e:
                return JsonResponse({'status': 'error', 'title': 'Erro ao fechar Caixa', 'message': str(e)}, status=400)
        elif action == 'create':
            try:
                if Cashier.objects.filter(status='open').exists():
                    return JsonResponse({'status': 'warning', 'title': 'Abertura de Caixa', 'message': 'Já existe um caixa aberto!'}, status=400)
                last_cashier = Cashier.objects.order_by('-created_at').first()
                new_cashier = Cashier.objects.create(
                    opening_balance=last_cashier.closing_balance if last_cashier else 0,
                    status='open',
                )
                return JsonResponse({'status': 'success', 'title': 'Abertura de Caixa', 'message': 'Caixa aberto com sucesso!'}, status=201)
            except Exception as e:
                return JsonResponse({'status': 'error', 'title': 'Erro ao abrir caixa', 'message': f'{e}'}, status=400)


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
            'student', 'plan').filter(paid=True)
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

            # Criar função para rodar em segundo plano e emitir a nota
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
