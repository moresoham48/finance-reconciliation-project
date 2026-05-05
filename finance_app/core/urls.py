from django.urls import path
from .views import final_ledger_api, summary_api, reconciliation_api, category_breakdown

urlpatterns = [
    path('final-ledger/', final_ledger_api),
    path('summary/', summary_api),
    path('reconciliation/', reconciliation_api),
    path('category/', category_breakdown),
]