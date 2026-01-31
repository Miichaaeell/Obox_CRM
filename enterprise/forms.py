from django import forms

from enterprise.models import (
    Bill,
    Enterprise,
    Installments,
    NFSe,
    StatusBill,
    TypeBill,
)


class EnterpriseForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = "__all__"
        fields_exclude = ["created_at", "updated_at"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "cnpj": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "cep": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "state": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "cnae_code": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "service_code": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "description_service": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 4,
                }
            ),
        }


class StatusBillForm(forms.ModelForm):
    class Meta:
        model = StatusBill
        fields = ["status"]
        widgets = {
            "status": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class TypeBillForm(forms.ModelForm):
    class Meta:
        model = TypeBill
        fields = ["type_bill"]
        widgets = {
            "type_bill": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ["description", "value", "due_date", "status", "payment_method"]
        widgets = {
            "description": forms.TextInput(
                attrs={"class": "border-b", "required": True}
            ),
            "value": forms.NumberInput(
                attrs={
                    "class": "border-b",
                    "placeholder": "RS 200000",
                    "required": True,
                }
            ),
            "due_date": forms.DateInput(
                attrs={"class": "border-b", "type": "date", "required": True}
            ),
            "payment_method": forms.RadioSelect(
                attrs={
                    "class": "sr-only",
                    "x-model": "selectedOpption",
                    "required": True,
                }
            ),
        }


class NFSeForm(forms.ModelForm):
    class Meta:
        model = NFSe
        fields = "__all__"
        fields_exclude = ["created_at", "updated_at"]
        widgets = {
            "student": forms.Select(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "issue_date": forms.DateInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "type": "date",
                }
            ),
            "uuid_nfse": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "link_pdf": forms.URLInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "link_xml": forms.URLInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "reference_month": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "type": "month",
                }
            ),
        }


class InstallmentsForm(forms.ModelForm):
    class Meta:
        model = Installments
        fields = ["quantity_installments"]
        widgets = {
            "quantity_installments": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                }
            ),
        }
