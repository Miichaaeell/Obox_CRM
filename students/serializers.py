from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from students.models import Student, StatusStudent, MonthlyFee, Payment, History


class StudentSerializer(serializers.ModelSerializer):
    feeid = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Student
        fields = '__all__'

    def update(self, instance, validated_data):
        _ = validated_data.pop('feeid', None)
        status = validated_data.pop('status', None)

        try:
            if status:
                with transaction.atomic():
                    fees = MonthlyFee.objects.filter(student=instance, paid=False)
                    totfees = fees.count()
                    fees.delete()

                    History.objects.create(
                        student=instance,
                        status=status,
                        description=f'{totfees} Mensalidades excluídas'
                    )
        except Exception as e:
            print(f'Erro no studant serializer {e}')

        if status:
            validated_data['status'] = status

        return super().update(instance, validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'value', 'quantity_installments']
        read_only_fields = ["monthlyfee", 'id']


class MonthlyFeeSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, write_only=True, required=True)
    plan = serializers.CharField(
        source='student.plan.name_plan', read_only=True,)

    class Meta:
        model = MonthlyFee
        fields = (
            'plan',
            'student_name',
            'discount_percent',
            'discount_value',
            'amount',
            'payments',
        )

    def update(self, instance, validated_data):
        payments = validated_data.pop('payments', [])

        with transaction.atomic():
            instance = super().update(instance, validated_data)
            instance.paid = True
            instance.date_paid = datetime.now().date()
            instance.save()
            instance.payments.all().delete()
            for payment in payments:
                Payment.objects.create(
                    montlhyfee=instance,
                    **payment
                )
        return instance


class StatusStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusStudent
        fields = '__all__'
