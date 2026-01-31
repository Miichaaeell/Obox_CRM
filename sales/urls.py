from django.urls import path

from sales.views import (
    IntflowCreateView,
    ProductCreateView,
    ProductListView,
    ProductUpdateView,
    StockDashboradView,
)

urlpatterns = [
    path("products/", ProductListView.as_view(), name="list_product"),
    path("products_create/", ProductCreateView.as_view(), name="create_product"),
    path(
        "products_update/<int:pk>/", ProductUpdateView.as_view(), name="update_product"
    ),
    path("stock/", StockDashboradView.as_view(), name="list_stock"),
    path("intflow_create/", IntflowCreateView.as_view(), name="create_intflow"),
]
