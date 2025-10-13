import json
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


from core.uploadfile import upload_file
from enterprise.models import Installments, PaymentMethod, Plan
from students.forms import StatusStudentForm, StudentForm
from students.serializers import StudentSerializer
from students.serializers import (
    MonthlyFeeSerializer,
    PaymentSerializer,
    StatusStudentSerializer,
)
from students.models import Frequency, History, MonthlyFee, StatusStudent, Student, Payment


# Views for Student model


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'list_students.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().select_related('status', 'plan')
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(cpf_cnpj__icontains=search_query) |
                Q(phone_number__icontains=search_query)
            )

        filter_value = (self.request.GET.get('filter') or '').lower()
        today = timezone.now().date()

        if filter_value == 'ativo':
            queryset = queryset.filter(status__status__iexact='ATIVO')
        elif filter_value == 'inativo':
            queryset = queryset.filter(status__status__iexact='INATIVO')
        elif filter_value == 'avencer':
            upcoming_limit = today + timedelta(days=10)
            queryset = queryset.filter(
                monthly_fees__paid=False,
                monthly_fees__due_date__range=(today, upcoming_limit)
            )
        elif filter_value == 'atrasado':
            queryset = queryset.filter(
                monthly_fees__paid=False,
                monthly_fees__due_date__lt=today
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_filter'] = self.request.GET.get(
            'filter', 'all') or 'all'
        context['search_query'] = self.request.GET.get('search', '')
        context['list_url'] = reverse('list_student')
        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('list_student')

    def get_context_data(self, **kwargs):
        today = datetime.now()
        context = super().get_context_data(**kwargs)
        context['payment_methods'] = PaymentMethod.objects.filter(
            applies_to__icontains='students')
        context['today'] = today
        context['plans'] = json.dumps(list(
            Plan.objects.values('id', 'price')), cls=DjangoJSONEncoder)
        context['quantity_installments'] = Installments.objects.all()
        return context

    @transaction.atomic
    def form_valid(self, form):
        today = datetime.now()
        studant_instance = form.save(commit=False)
        studant_instance.status = StatusStudent.objects.get(
            status__iexact='ATIVO')
        studant_instance.due_date = int(today.day)
        studant_instance.observation = str('Novo Aluno')
        studant_instance.save()
        amount = self.request.POST.get(
            'value_receiver').replace('R', '').replace('$', '').replace(',', '.')
        discount_percent = self.request.POST.get('percent_discount')
        discount_value = self.request.POST.get('discount_value')
        quantity_installments = self.request.POST.get('quantity_installments')
        monthlyfe = MonthlyFee.objects.create(
            student=studant_instance,
            student_name=studant_instance.name,
            amount=amount,
            due_date=today,
            reference_month=f'{today.month}/{today.year}',
            paid=True,
            date_paid=today,
            discount_value=discount_value if discount_value else 0,
            discount_percent=discount_percent if discount_percent else 0,
            plan=studant_instance.plan
        )
        import json
        payments_json = self.request.POST.get('payments') or '[]'
        payments_data = json.loads(payments_json)
        payments_create = [
            Payment(
                montlhyfee=monthlyfe,
                payment_method=payment.get('payment_method') or payment.get('method') or '',
                value=Decimal(str(payment.get('value') or payment.get('receive_value') or 0)),
                quantity_installments=int(payment.get('quantity_installments') or payment.get('installments') or 1)
            )
            for payment in payments_data
        ]
        Payment.objects.bulk_create(payments_create)
        return redirect(self.success_url)


class StudentDetailView(DetailView):
    model = Student
    template_name = 'detail_student.html'
    context_object_name = 'obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Detalhes'
        context['sufix_url'] = 'student'
        context['historys'] = History.objects.filter(student=self.object)
        context['frequency'] = Frequency.objects.filter(student=self.object)
        context['monthlyfees'] = MonthlyFee.objects.filter(student=self.object)
        context['payment_methods'] = PaymentMethod.objects.all()
        context['form'] = StudentForm(instance=self.object)
        context['plans'] = json.dumps(
            list(Plan.objects.values('id', 'price')),
            cls=DjangoJSONEncoder
        )
        context['today'] = timezone.now()
        context['title_card'] = 'Ativar aluno'
        return context

# Views for frequence studant


class FrequenceStudentView(LoginRequiredMixin, View):
    template_name = 'frequence.html'
    students = Student.objects.filter(status__status__iexact='ativo')
    context = {'students': students}

    def get(self, request):
        return render(request, self.template_name, context=self.context)

    # Views for StatusStudent model


class StatusStudentListView(LoginRequiredMixin, ListView):
    model = StatusStudent
    template_name = 'components/_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Status dos Alunos'
        context['sufix_url'] = 'status'
        return context


class StatusStudentCreateView(LoginRequiredMixin, CreateView):
    model = StatusStudent
    form_class = StatusStudentForm
    template_name = 'components/_create_update.html'
    success_url = reverse_lazy('list_status')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Status'
        context['sufix_url'] = 'status'
        return context


class StatusStudentUpdateView(LoginRequiredMixin, UpdateView):
    model = StatusStudent
    form_class = StatusStudentForm
    template_name = 'components/_create_update.html'
    success_url = reverse_lazy('list_status')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Status'
        context['sufix_url'] = 'status'
        return context


class UploadFileView(View):
    def post(self, request):
        file = request.FILES['file']
        response = upload_file(file)
        match response['status_code']:
            case '201':
                messages.success(request, response['message'])
            case '422':
                messages.error(request, response['message'])
            case '400':
                messages.error(request, response['message'])
        return redirect('list_student')


# Views de API

class MonthlyFeeRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MonthlyFee.objects.all()
    serializer_class = MonthlyFeeSerializer


class StudentRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class StatusStudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = StatusStudent.objects.all()
    serializer_class = StatusStudentSerializer
