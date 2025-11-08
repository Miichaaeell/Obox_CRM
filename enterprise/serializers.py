from rest_framework import serializers

from enterprise.models import Bill, Plan


class BillSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bill
        fields = '__all__'


class NFESerializer(serializers.Serializer):
    student = serializers.ListField(
        child=serializers.DictField()
    )
    description = serializers.CharField()
    reference_month = serializers.CharField()
    
    
class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = '__all__'
