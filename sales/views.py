from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from sales.forms import IntflowForm, ProductForm
from sales.models import Intflow, Product, ProductStock


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = "components/_list.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Produtos"
        context["sufix_url"] = "product"
        return context


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "components/_create_update.html"
    success_url = reverse_lazy("list_product")
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Produtos"
        context["sufix_url"] = "product"
        return context


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "components/_create_update.html"
    success_url = reverse_lazy("list_product")
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Produtos"
        context["sufix_url"] = "product"
        return context


class StockDashboradView(LoginRequiredMixin, ListView):
    model = ProductStock
    template_name = "stock_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_stock"] = ProductStock.objects.all().aggregate(
            total=Sum("quantity")
        )["total"]
        return context


class IntflowCreateView(LoginRequiredMixin, CreateView):
    model = Intflow
    form_class = IntflowForm
    template_name = "components/_create_update.html"
    success_url = reverse_lazy("list_stock")
    context_object_name = "intflow"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Entrada de Produto"
        context["sufix_url"] = "stock"
        return context
