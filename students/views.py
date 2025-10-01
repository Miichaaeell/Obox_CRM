from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView, View, TemplateView
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Student, StatusStudent, History, Frequency, MonthlyFee
from .forms import StudentForm, StatusStudentForm
from enterprise.models import Plan, Installments
from enterprise.models import PaymentMethod
from datetime import datetime
import json
from core.uploadfile import upload_file

from datetime import datetime
# Views for Student model


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'list_students.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search', None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) |
                                       Q(cpf_cnpj__icontains=search_query) |
                                       Q(phone_number__icontains=search_query))
        return queryset


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('list_student')

    def get_context_data(self, **kwargs):
        today = datetime.now()
        context = super().get_context_data(**kwargs)
        context['title'] = 'Aluno'
        context['sufix_url'] = 'student'
        context['payment_methods'] = PaymentMethod.objects.all()
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


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'components/_create_update.html'
    context_object_name = 'obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Aluno'
        context['sufix_url'] = 'student'
        return context

    def get_success_url(self):
        return reverse_lazy('detail_student', kwargs={'pk': self.object.pk})


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
