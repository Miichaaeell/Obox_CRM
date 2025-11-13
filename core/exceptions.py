from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db.models.deletion import ProtectedError

def custom_exception_handler(exc, context):
    resp = exception_handler(exc, context)
    if isinstance(exc, ProtectedError):
        return Response({"detail": "Não é possível excluir: há dependências relacionadas."},
                        status=status.HTTP_409_CONFLICT)
    return resp
