from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Avg, Q
from .models import Admission
from .serializers import AdmissionSerializer

# --- PAGINATION ---
class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination to prevent API timeouts by limiting 
    large datasets to 10 records per page.
    """
    page_size = 10

# 1. CREATE ENDPOINT (POST)
class AdmissionCreateView(generics.CreateAPIView):
    """
    Endpoint Requirement: POST
    Logic: Allows for the manual registration of new patient admission records.
    """
    queryset = Admission.objects.all()
    serializer_class = AdmissionSerializer

# 2. FILTER + AGGREGATION (GET)
class HighRiskDemographicStats(APIView):
    """
    Endpoint Requirement: Aggregation & Filtering
    Logic: Analyzes the average hospital stay for 'High Risk' seniors.
    Data Sync: '>=60' age tokens and 'ELEVATED' HbA1c strings.
    """
    def get(self, request):
        # Filter by age group and HbA1c level, then aggregate
        stats = Admission.objects.filter(
            hba1c__iexact='ELEVATED', 
            age_group='>=60' 
        ).aggregate(
            total_cases=Count('id'),
            average_stay_duration=Avg('hospital_stay')
        )
        return Response(stats)

# 3. COMPLEX FILTER + PAGINATION (GET)
class ChronicReadmissionList(generics.ListAPIView):
    """
    Endpoint Requirement: Complex Filtering (Q Objects) & Pagination
    Logic: Identifies 'Chronic' patients (High visits OR high med load) 
           who were subsequently readmitted.
    """
    serializer_class = AdmissionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Q objects allow for OR (|) logic within the database query
        return Admission.objects.filter(
            (Q(patient_visits__gt=5) | Q(num_medications__gt=20)),
            readmitted=True
        ).order_by('-admission_date')

# 4. GROUPED AGGREGATION (GET)
class InsulinMedicationSummary(APIView):
    """
    Endpoint Requirement: Aggregation (Annotate/Group By)
    Logic: Summarizes the medication burden for readmitted patients,
           grouped by their insulin dosage levels.
    """
    def get(self, request):
        # .values() acts as a 'GROUP BY' in SQL
        # .annotate() calculates math for each group
        stats = Admission.objects.filter(readmitted=True).values('insulin_level').annotate(
            patient_count=Count('id'),
            average_medication_count=Avg('num_medications')
        ).order_by('-patient_count')
        return Response(stats)

# 5. MULTI-FIELD CLINICAL FILTER (GET)
class ComplexMedicalFilterList(generics.ListAPIView):
    """
    Endpoint Requirement: Multi-field Filtering
    Logic: Filters for severe cases defined by active diabetes medication, 
           high diagnosis count (>5), and extended stays (>3 days).
    """
    serializer_class = AdmissionSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Admission.objects.filter(
            diabetes_med=True,
            num_diagnosis__gt=5,
            hospital_stay__gt=3
        ).order_by('-hospital_stay')

# 6. GENDER CLINICAL ANALYSIS (GET)
class GenderClinicalAnalysis(APIView):
    """
    Endpoint Requirement: Database-wide Aggregation
    Logic: Provides a comparative clinical summary between genders, 
           calculating averages for stays and diagnosis complexity.
    """
    def get(self, request):
        # Groups the entire database by the 'sex' field (MALE/FEMALE)
        analysis = Admission.objects.values('sex').annotate(
            total_records=Count('id'),
            avg_stay=Avg('hospital_stay'),
            avg_diagnosis_count=Avg('num_diagnosis')
        )
        return Response(analysis)