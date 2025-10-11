from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

from django.db import transaction
from rest_framework import serializers
from students.models import Student, StatusStudent, MonthlyFee, Payment


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'


class MonthlyFeePaymentDetailSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(
        source='student.plan.name_plan', read_only=True)
    base_amount = serializers.SerializerMethodField()
    final_amount = serializers.DecimalField(
        source='amount', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = MonthlyFee
        fields = [
            'id',
            'student_name',
            'plan',
            'base_amount',
            'final_amount',
            'discount_percent',
            'discount_value',
            'reference_month'
        ]

    def get_base_amount(self, obj):
        if obj.plan and obj.plan.price is not None:
            return obj.plan.price

        if obj.discount_value:
            return (obj.amount or Decimal('0')) + obj.discount_value

        return obj.amount


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'value', 'quantity_installments']
        read_only_fields = ["monthlyfee", 'id']


class MonthlyFeePaymentUpdateSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, write_only=True, required=True)

    class Meta:
        model = MonthlyFee
        fields = (
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


class StudentInactivationSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    reason = serializers.CharField()

    def validate_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError(
                'Informe o motivo da inativação.')
        return value.strip()

    def validate(self, attrs):
        student_id = attrs.get('student_id')
        try:
            student = Student.objects.select_related(
                'status').get(pk=student_id)
        except Student.DoesNotExist as exc:
            raise serializers.ValidationError(
                {'student_id': 'Aluno não encontrado.'}) from exc

        inactive_status = StatusStudent.objects.filter(
            status__iexact='INATIVO').first()
        if not inactive_status:
            raise serializers.ValidationError(
                {'student_id': 'Status inativo não está configurado.'})

        attrs['student'] = student
        attrs['inactive_status'] = inactive_status
        return attrs

    def save(self):
        student = self.validated_data['student']
        inactive_status = self.validated_data['inactive_status']
        reason = self.validated_data['reason']

        student.status = inactive_status
        student.observation = reason
        student.save(update_fields=['status', 'observation', 'updated_at'])

        deleted_count, _ = MonthlyFee.objects.filter(
            student=student, paid=False).delete()
        self.context['deleted_count'] = deleted_count
        return student
