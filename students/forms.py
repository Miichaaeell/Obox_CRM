from datetime import datetime

from django import forms

from students.models import Frequency, History, MonthlyFee, StatusStudent, Student


class StatusStudentForm(forms.ModelForm):
    class Meta:
        model = StatusStudent
        fields = ['status']
        widgets = {
            'status': forms.TextInput(attrs={
                "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
        }


today = datetime.now().day


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'cpf_cnpj', 'date_of_birth', 'phone_number', 'plan']
        widgets = {
            'name': forms.TextInput(attrs={"class": "text-gray-700 w-full border-b border-gray-400 focus:outline-none"}),
            'cpf_cnpj': forms.TextInput(attrs={"class": "text-gray-700 w-32 border-b border-gray-400 focus:outline-none", "help_text": "Ex. 12345678910", "x-data": "",
                                               "x-mask:dynamic": "$input.length <= 14 ? '999.999.999-99' : '99.999.999/9999-99'",
                                               "placeholder": "Digite CPF ou CNPJ", }),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'text-gray-700 w-32 border-b border-gray-400 focus:outline-none'}),
            'phone_number': forms.TextInput(attrs={"class": "text-gray-700 w-32 border-b border-gray-400 focus:outline-none", "help_text": "19999999999", "placeholder": '19999999999', 'required': True, "x-data": "", "x-mask": "(99) 9 9999-9999"}),
            'status': forms.Select(attrs={
                "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'due_date': forms.NumberInput(attrs={'class': 'text-gray-700 w-32 border-b border-gray-400 focus:outline-none', 'value': today, 'disabled': True}),
            'plan': forms.Select(attrs={'class': "text-gray-700 w-32 bg-transparent border-b border-gray-400 focus:outline-none",
                                        }),
            'observation': forms.Textarea(attrs={
                "placeholder": "Ex: Novo aluno, vem por indicação do João.",
                "class": "mt-1 block w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
        }


class FrequencyForm(forms.ModelForm):
    class Meta:
        model = Frequency
        fields = ['student']
        widgets = {
            'student': forms.Select(attrs={
                "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
        }


class HistoryForm(forms.ModelForm):
    class Meta:
        model = History
        fields = ['student', 'status', 'description']
        widgets = {
            'student': forms.Select(attrs={
                "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'status': forms.Select(attrs={
                "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'description': forms.Textarea(attrs={
                "placeholder": "Descrição da ação realizada",
                "class": "mt-1 block w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
        }


class MonthlyFeeForm(forms.ModelForm):
    class Meta:
        model = MonthlyFee
        fields = ['student', 'amount', 'due_date',
                  'reference_month', 'paid',]
        widgets = {
            'student': forms.Select(attrs={
                "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
            }),
            'amount': forms.NumberInput(attrs={"class": "w-full px-4 py-2 rounded-lg border border-gray-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500"}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 rounded-lg  border border-gray-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}),
            'reference_month': forms.DateInput(attrs={'type': 'month', 'class': 'w-full px-4 py-2 rounded-lg  border border-gray-700 focus:ring-2 focus:ring-purple-500 focus:border-purple-500'}),
            'paid': forms.CheckboxInput(attrs={"class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"}),

        }
