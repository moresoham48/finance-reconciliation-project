from rest_framework import serializers
from .models import FinalLedger

class FinalLedgerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalLedger
        fields = '__all__'