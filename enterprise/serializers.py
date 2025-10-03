from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone
from rest_framework import serializers

from students.models import MonthlyFee, Student, StatusStudent
from .models import Bill, PaymentMethod


class BillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bill
        fields = '__all__'
        

class NFESerializer(serializers.Serializer):
    student = serializers.ListField(
        child = serializers.DictField()
    )
    description = serializers.CharField()
    reference_month = serializers.CharField()
    
    
class MonthlyFeePaymentDetailSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(source='student.plan.name_plan', read_only=True)
    base_amount = serializers.SerializerMethodField()
    final_amount = serializers.DecimalField(source='amount', max_digits=10, decimal_places=2, read_only=True)
    payment_methods = serializers.SerializerMethodField()
    current_payment_method = serializers.CharField(source='payment_method', read_only=True)

    class Meta:
        model = MonthlyFee
        fields = [
            'id',
            'plan',
            'base_amount',
            'final_amount',
            'discount_percent',
            'discount_value',
            'quantity_installments',
            'payment_methods',
            'current_payment_method',
        ]

    def get_base_amount(self, obj):
        if obj.plan and obj.plan.price is not None:
            return obj.plan.price

        if obj.discount_value:
            return (obj.amount or Decimal('0')) + obj.discount_value

        return obj.amount

    def get_payment_methods(self, obj):
        methods = PaymentMethod.objects.filter(applies_to__icontains='students')
        return [{'id': method.id, 'name': method.method} for method in methods]


class MonthlyFeePaymentUpdateSerializer(serializers.ModelSerializer):
    payment_method = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(applies_to__icontains='students'),
        write_only=True,
    )
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = MonthlyFee
        fields = (
            'payment_method',
            'discount_percent',
            'discount_value',
            'final_amount',
            'quantity_installments',
        )

    def validate(self, attrs):
        instance = self.instance
        base_amount = self._get_base_amount(instance)

        discount_percent = attrs.get('discount_percent', Decimal('0'))
        discount_value = attrs.get('discount_value', Decimal('0'))
        final_amount = attrs['final_amount']

        if discount_percent is None:
            discount_percent = Decimal('0')
        if discount_value is None:
            discount_value = Decimal('0')

        if discount_value < 0:
            raise serializers.ValidationError({'discount_value': 'O desconto não pode ser negativo.'})

        if discount_percent < 0:
            raise serializers.ValidationError({'discount_percent': 'O desconto não pode ser negativo.'})
        if discount_percent > 100:
            raise serializers.ValidationError({'discount_percent': 'O desconto não pode ser maior que 100%.'})

        expected_discount = (base_amount * discount_percent / Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if discount_value and abs(expected_discount - discount_value) > Decimal('0.05'):
            raise serializers.ValidationError({'discount_value': 'Valor e porcentagem de desconto não conferem com o valor base.'})

        calculated_final = (base_amount - discount_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        if calculated_final < 0:
            raise serializers.ValidationError({'final_amount': 'O valor final não pode ser negativo.'})

        if abs(calculated_final - final_amount) > Decimal('0.05'):
            raise serializers.ValidationError({'final_amount': 'O valor final não confere com os dados informados.'})

        attrs['discount_percent'] = discount_percent.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        attrs['discount_value'] = discount_value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        attrs['final_amount'] = final_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return attrs

    def update(self, instance, validated_data):
        payment_method = validated_data.pop('payment_method')
        final_amount = validated_data.pop('final_amount')

        instance.amount = final_amount
        instance.discount_percent = validated_data.get('discount_percent', Decimal('0'))
        instance.discount_value = validated_data.get('discount_value', Decimal('0'))
        quantity_installments = validated_data.get('quantity_installments')
        if quantity_installments is not None:
            instance.quantity_installments = quantity_installments
        instance.payment_method = payment_method.method.upper()
        instance.paid = True
        instance.date_paid = timezone.localdate()
        instance.save(update_fields=[
            'amount',
            'discount_percent',
            'discount_value',
            'quantity_installments',
            'payment_method',
            'paid',
            'date_paid'
        ])
        return instance

    def validate_quantity_installments(self, value):
        if value in (None, ''):
            return value

        if isinstance(value, str):
            value = value.lower().replace('x', '').strip()

        try:
            value_int = int(value)
        except (TypeError, ValueError):
            raise serializers.ValidationError('Informe um número inteiro válido de parcelas.')

        if value_int <= 0:
            raise serializers.ValidationError('O número de parcelas deve ser maior que zero.')

        return value_int

    @staticmethod
    def _get_base_amount(instance):
        if instance.plan and instance.plan.price is not None:
            return instance.plan.price

        if instance.discount_value:
            return (instance.amount or Decimal('0')) + instance.discount_value

        return instance.amount or Decimal('0')


class StudentInactivationSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    reason = serializers.CharField()

    def validate_reason(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('Informe o motivo da inativação.')
        return value.strip()

    def validate(self, attrs):
        student_id = attrs.get('student_id')
        try:
            student = Student.objects.select_related('status').get(pk=student_id)
        except Student.DoesNotExist as exc:
            raise serializers.ValidationError({'student_id': 'Aluno não encontrado.'}) from exc

        inactive_status = StatusStudent.objects.filter(status__iexact='INATIVO').first()
        if not inactive_status:
            raise serializers.ValidationError({'student_id': 'Status inativo não está configurado.'})

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

        deleted_count, _ = MonthlyFee.objects.filter(student=student, paid=False).delete()
        self.context['deleted_count'] = deleted_count
        return student
