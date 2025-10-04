import json
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.shortcuts import HttpResponse, redirect, render, get_object_or_404
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
from enterprise.serializers import (
    MonthlyFeePaymentDetailSerializer,
    MonthlyFeePaymentUpdateSerializer,
    StudentInactivationSerializer,
)
from students.models import Frequency, History, MonthlyFee, StatusStudent, Student


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

    def form_valid(self, form):
        today = datetime.now()
        studant_instance = form.save(commit=False)
        studant_instance.status = StatusStudent.objects.get(
            status__iexact='ATIVO')
        studant_instance.due_date = int(today.day)
        studant_instance.observation = str('Novo Aluno')
        studant_instance.save()
        amount = self.request.POST.get('value_receiver')
        discount_percent = self.request.POST.get('percent_discount')
        discount_value = self.request.POST.get('discount_value')
        payment_method = self.request.POST.get('payment_method')
        quantity_installments = self.request.POST.get('quantity_installments')
        MonthlyFee.objects.create(
            student=studant_instance,
            amount=amount,
            due_date=today,
            reference_month=f'{today.month}/{today.year}',
            paid=True,
            payment_method=payment_method,
            quantity_installments=int(quantity_installments.replace('x', '')),
            date_paid=today,
            discount_value=discount_value if discount_value else 0,
            discount_percent=discount_percent if discount_percent else 0,
            plan=studant_instance.plan
        )
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


class MonthlyFeeUpdateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        monthly_fee_id = kwargs.get('pk')
        monthly_fee = MonthlyFee.objects.get(id=monthly_fee_id)
        return HttpResponse(f"Marcar mensalidade {monthly_fee} como paga")

    def post(self, request, *args, **kwargs):
        monthly_fee_id = request.POST.get("monthlyfee_id")
        payment_method = request.POST.get('method')
        monthly_fee = MonthlyFee.objects.get(id=monthly_fee_id)
        monthly_fee.paid = True
        monthly_fee.payment_method = payment_method
        monthly_fee.save()
        return redirect('detail_student', pk=monthly_fee.student.pk)


class MonthlyFeeDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        monthly_fee_id = request.POST.get("monthlyfee_id")
        monthly_fee = MonthlyFee.objects.get(id=monthly_fee_id)
        student_id = monthly_fee.student
        History.objects.create(
            student=student_id,
            status=student_id.status,
            description=f'Mensalidade de {monthly_fee.reference_month} no valor de R$ {monthly_fee.amount} cancelada.'
        )
        monthly_fee.delete()
        return redirect('detail_student', pk=student_id.id)


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


#Views de API

class MonthlyFeePaymentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        fee = get_object_or_404(MonthlyFee, pk=pk)
        serializer = MonthlyFeePaymentDetailSerializer(fee)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MonthlyFeePaymentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        monthlyfee_id = request.data.get('monthlyfee_id')
        if not monthlyfee_id:
            return Response(
                {
                    'success': False,
                    'message': 'Informe a mensalidade a ser atualizada.',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        fee = get_object_or_404(MonthlyFee, pk=monthlyfee_id)
        serializer = MonthlyFeePaymentUpdateSerializer(fee, data=request.data)

        if serializer.is_valid():
            updated_fee = serializer.save()
            detail = MonthlyFeePaymentDetailSerializer(updated_fee)
            return Response(
                {
                    'success': True,
                    'message': 'Pagamento registrado com sucesso.',
                    'payment': detail.data,
                }
            )

        return Response(
            {
                'success': False,
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class StudentInactivationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = StudentInactivationSerializer(data=request.data)

        if serializer.is_valid():
            student = serializer.save()
            message = f'Aluno {student.name} inativado com sucesso.'
            return Response(
                {
                    'success': True,
                    'message': message,
                    'deleted_count': serializer.context.get('deleted_count', 0),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                'success': False,
                'message': 'Não foi possível inativar o aluno.',
                'errors': serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

class StudentRetriveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    