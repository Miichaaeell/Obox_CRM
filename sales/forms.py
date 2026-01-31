from django import forms

from sales.models import Intflow, Product, ProductStock, Sale


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "price"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 4,
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class ProductStockForm(forms.ModelForm):
    class Meta:
        model = ProductStock
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }


class IntflowForm(forms.ModelForm):
    class Meta:
        model = Intflow
        fields = ["product", "quantity", "description"]
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 4,
                }
            ),
        }


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            "product",
            "value_unitary",
            "quantity",
            "discount_value",
            "discount_percent",
            "payment_method",
            "total_price",
        ]
        widgets = {
            "product": forms.Select(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "value_unitary": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "quantity": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "discount_value": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "discount_percent": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "payment_method": forms.Select(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "total_price": forms.NumberInput(
                attrs={
                    "class": "mt-1 block w-full px py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
        }
