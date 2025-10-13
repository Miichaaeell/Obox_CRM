import json
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
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


class StudentActivateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        student_payload = request.data.get('student') or {}
        payment_payload = request.data.get('payment') or {}
        payments_payload = payment_payload.get('payments') or []

        if not payments_payload:
            return Response(
                {'message': 'Adicione ao menos uma forma de pagamento.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        active_status = StatusStudent.objects.filter(
            status__iexact='ATIVO').first()
        if not active_status:
            return Response(
                {'message': 'Status "ATIVO" não está configurado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def to_decimal(value, default='0.00'):
            try:
                return Decimal(str(value)).quantize(Decimal('0.01'))
            except (InvalidOperation, TypeError, ValueError):
                try:
                    return Decimal(default).quantize(Decimal('0.01'))
                except (InvalidOperation, TypeError, ValueError):
                    return None

        amount = to_decimal(payment_payload.get('amount'))
        if amount is None or amount <= 0:
            return Response(
                {'message': 'Valor total do pagamento inválido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        discount_percent = to_decimal(
            payment_payload.get('discount_percent'), default='0.00')
        discount_value = to_decimal(
            payment_payload.get('discount_value'), default='0.00')
        if discount_percent is None or discount_value is None:
            return Response(
                {'message': 'Valores de desconto inválidos.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        processed_payments = []
        for item in payments_payload:
            method = (item.get('payment_method') or '').strip()
            if not method:
                return Response(
                    {'message': 'Informe o método de pagamento.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment_value = to_decimal(item.get('value'))
            if payment_value is None or payment_value <= 0:
                return Response(
                    {'message': f'Valor inválido para o pagamento "{method}".'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                installments = int(item.get('quantity_installments') or 1)
            except (TypeError, ValueError):
                installments = 1
            processed_payments.append(
                (method, payment_value, max(1, installments)))

        total_received = sum(value for _, value, _ in processed_payments)
        if abs(total_received - amount) > Decimal('0.01'):
            return Response(
                {'message': 'A soma dos pagamentos difere do valor devido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        plan_input = student_payload.get('plan')
        plan_obj = None
        if plan_input not in (None, '', 'null'):
            try:
                plan_id = int(plan_input)
            except (TypeError, ValueError):
                return Response(
                    {'message': 'Plano informado é inválido.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            plan_obj = Plan.objects.filter(pk=plan_id).first()
            if not plan_obj:
                return Response(
                    {'message': 'Plano informado não foi encontrado.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        date_str = student_payload.get('date_of_birth')
        birth_date = None
        clear_birth_date = False
        if date_str is not None:
            if date_str == '':
                clear_birth_date = True
            else:
                try:
                    birth_date = datetime.strptime(
                        date_str, '%Y-%m-%d').date()
                except ValueError:
                    return Response(
                        {'message': 'Data de nascimento inválida.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        name_value = (student_payload.get('name') or '').strip()
        cpf_value = student_payload.get('cpf_cnpj')
        phone_value = student_payload.get('phone_number')

        with transaction.atomic():
            MonthlyFee.objects.filter(student=student, paid=False).delete()

            if plan_obj:
                student.plan = plan_obj

            if name_value:
                student.name = name_value

            if cpf_value:
                student.cpf_cnpj = cpf_value

            if phone_value is not None:
                student.phone_number = phone_value

            if date_str is not None:
                student.date_of_birth = None if clear_birth_date else birth_date

            student.status = active_status
            student.observation = 'Aluno reativado'
            student.save()

            MonthlyFee.objects.filter(student=student, paid=False).delete()

            now = timezone.now()
            monthly_fee = MonthlyFee.objects.create(
                student=student,
                student_name=student.name,
                amount=amount,
                due_date=now.date(),
                reference_month=f'{now.month}/{now.year}',
                paid=True,
                date_paid=now.date(),
                discount_value=discount_value,
                discount_percent=discount_percent,
                plan=student.plan,
            )

            Payment.objects.bulk_create([
                Payment(
                    montlhyfee=monthly_fee,
                    payment_method=method,
                    value=value,
                    quantity_installments=installments,
                )
                for method, value, installments in processed_payments
            ])

        return Response(
            {
                'message': 'Aluno reativado com sucesso.',
                'monthly_fee_id': monthly_fee.id,
            },
            status=status.HTTP_200_OK,
        )


class StudentRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class PaymentListCreateAPIView(generics.ListCreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class StatusStudentListCreateAPIView(generics.ListCreateAPIView):
    queryset = StatusStudent.objects.all()
    serializer_class = StatusStudentSerializer
