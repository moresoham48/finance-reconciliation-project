from django.shortcuts import render

import pandas as pd
from .models import BankStatement
from .models import InternalLedger
from fuzzywuzzy import fuzz

from django.db.models import Sum

def upload_bank_csv(file):
    df = pd.read_csv(file)

    for _, row in df.iterrows():
        BankStatement.objects.create(
            date=row['date'],
            narration=row['narration'],
            amount=row['amount'],
            type=row['type']
        )




def upload_internal_csv(file):
    df = pd.read_csv(file)

    df['date'] = pd.to_datetime(df['date'], dayfirst=True)

    for _, row in df.iterrows():
        InternalLedger.objects.create(
            date=row['date'],
            description=row['description'],
            amount=row['amount'],
            category=row['category']
        )

from fuzzywuzzy import fuzz

def reconcile():
    bank_data = BankStatement.objects.all()
    ledger_data = InternalLedger.objects.all()

    matched = []
    unmatched_bank = []
    unmatched_ledger = list(ledger_data)

    for bank in bank_data:
        found = False

        for ledger in ledger_data:
            if bank.amount == ledger.amount:

                date_diff = abs((bank.date - ledger.date).days)

                similarity = fuzz.ratio(
                    bank.narration.lower(),
                    ledger.description.lower()
                )

                if date_diff <= 2 and similarity > 70:
                    matched.append((bank, ledger))
                    if ledger in unmatched_ledger:
                        unmatched_ledger.remove(ledger)
                    found = True
                    break

        if not found:
            unmatched_bank.append(bank)

    return matched, unmatched_bank, unmatched_ledger


from .models import FinalLedger

def create_final_ledger():
    matched, unmatched_bank, unmatched_ledger = reconcile()

    # matched records
    for bank, ledger in matched:
        FinalLedger.objects.create(
            date=bank.date,
            amount=bank.amount,
            category=ledger.category,
            source="both",
            reconciliation_status="matched"
        )

    # unmatched bank
    for bank in unmatched_bank:
        FinalLedger.objects.create(
            date=bank.date,
            amount=bank.amount,
            category="unknown",
            source="bank",
            reconciliation_status="unmatched"
        )

    # unmatched ledger
    for ledger in unmatched_ledger:
        FinalLedger.objects.create(
            date=ledger.date,
            amount=ledger.amount,
            category=ledger.category,
            source="internal",
            reconciliation_status="unmatched"
        )


from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FinalLedger
from .serializers import FinalLedgerSerializer

@api_view(['GET'])
def final_ledger_api(request):
    data = FinalLedger.objects.all()
    serializer = FinalLedgerSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def summary_api(request):
    total_credits = FinalLedger.objects.filter(source="both").aggregate(Sum('amount'))['amount__sum'] or 0
    total_debits = FinalLedger.objects.filter(source="bank").aggregate(Sum('amount'))['amount__sum'] or 0
    unmatched = FinalLedger.objects.filter(reconciliation_status="unmatched").aggregate(Sum('amount'))['amount__sum'] or 0

    return Response({
        "total_credits": total_credits,
        "total_debits": total_debits,
        "unmatched_amount": unmatched
    })

@api_view(['GET'])
def reconciliation_api(request):
    data = FinalLedger.objects.all()
    serializer = FinalLedgerSerializer(data, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_breakdown(request):
    data = FinalLedger.objects.values('category').annotate(total=Sum('amount'))
    return Response(data)