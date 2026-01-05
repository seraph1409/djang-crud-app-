from django.urls import path
from .views import home
from .api import (
    AdmissionCreateView, HighRiskDemographicStats, ChronicReadmissionList,
    InsulinMedicationSummary, ComplexMedicalFilterList, GenderClinicalAnalysis
)

urlpatterns = [
    path("", home, name="home"),
    path("api/data/add/", AdmissionCreateView.as_view(), name="admission-create"),
    path("api/analysis/demographic-stats/", HighRiskDemographicStats.as_view(), name="high-risk-stats"),
    path("api/analysis/chronic-readmissions/", ChronicReadmissionList.as_view(), name="chronic-list"),
    path("api/analysis/medication-insulin/", InsulinMedicationSummary.as_view(), name="insulin-summary"),
    path("api/analysis/complex-clinical/", ComplexMedicalFilterList.as_view(), name="complex-filter"),
    path("api/analysis/gender-metrics/", GenderClinicalAnalysis.as_view(), name="gender-analysis"),
]