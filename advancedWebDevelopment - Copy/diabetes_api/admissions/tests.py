import json
from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Admission
from .serializers import AdmissionSerializer
from .model_factories import AdmissionFactory

# ---------------------------------------------------------
# 1. SERIALIZER TESTS
# ---------------------------------------------------------
class AdmissionSerializerTest(APITestCase):
    """Tests to ensure the Serializer handles data conversion correctly."""

    def setUp(self):
        # Create a single record for serialization testing
        self.admission1 = AdmissionFactory.create(sex="MALE", age_group=">=60")
        self.serializer = AdmissionSerializer(instance=self.admission1)

    def tearDown(self):
        Admission.objects.all().delete()
        AdmissionFactory.reset_sequence(0)

    def test_serializerHasCorrectFields(self):
        """Verifies that all expected fields are present in the JSON output."""
        data = self.serializer.data
        expected_fields = set([
            'id', 'admission_date', 'race', 'sex', 'age_group', 
            'hospital_stay', 'hba1c', 'diabetes_med', 'admit_source', 
            'patient_visits', 'num_medications', 'num_diagnosis', 
            'insulin_level', 'readmitted'
        ])
        self.assertEqual(set(data.keys()), expected_fields)

    def test_serializerDataMatchesModel(self):
        """Checks if the data values are correctly translated by the serializer."""
        data = self.serializer.data
        self.assertEqual(data['sex'], "MALE")
        self.assertEqual(data['age_group'], ">=60")


# ---------------------------------------------------------
# 2. API ENDPOINT TESTS
# ---------------------------------------------------------
class AdmissionAPITest(APITestCase):
    """Tests for the API View logic, filtering, and aggregation."""

    def setUp(self):
        # Create 'High Risk' patient: Matches the API filter (ELEVATED + >=60)
        self.senior_high_risk = AdmissionFactory.create(
            age_group='>=60', 
            hba1c='ELEVATED', 
            hospital_stay=10
        )
        
        # Create 'Low Risk' patient: Should be IGNORED by the high-risk filter
        self.normal_patient = AdmissionFactory.create(
            age_group='<30', 
            hba1c='NORMAL', 
            hospital_stay=2,
            patient_visits=10, 
            readmitted=True
        )
        
        # Define URLs using names from urls.py
        self.create_url = reverse('admission-create')
        self.stats_url = reverse('high-risk-stats')
        self.chronic_list_url = reverse('chronic-list')

    def tearDown(self):
        # Clean database after every test
        Admission.objects.all().delete()

    def test_highRiskStatsReturnsCorrectAggregation(self):
        """Test if the Aggregation GET request correctly filters and calculates."""
        response = self.client.get(self.stats_url, format='json')
        self.assertEqual(response.status_code, 200)
        
        data = response.data
        # Math Check: Only 1 patient (senior_high_risk) should be counted
        self.assertEqual(data['total_cases'], 1)
        # Math Check: The average stay of that 1 patient is exactly 10.0
        self.assertEqual(data['average_stay_duration'], 10.0)

    def test_createAdmissionSuccessfully(self):
        """Test the POST endpoint to create a new record."""
        new_data = {
            "admission_date": "2023-05-05",
            "race": "Other",
            "sex": "FEMALE",
            "age_group": "<30",
            "hospital_stay": 2,
            "hba1c": "NORMAL",
            "diabetes_med": False,
            "admit_source": "Referral",
            "patient_visits": 0,
            "num_medications": 5,
            "num_diagnosis": 2,
            "insulin_level": "NONE",
            "readmitted": False
        }
        response = self.client.post(self.create_url, new_data, format='json')
        self.assertEqual(response.status_code, 201)
        
        # Verify the database now has 3 records (2 from setUp + 1 new)
        self.assertEqual(Admission.objects.count(), 3)

    def test_chronicListIsPaginated(self):
        """Test if the list endpoint returns paginated results."""
        response = self.client.get(self.chronic_list_url, format='json')
        self.assertEqual(response.status_code, 200)
        
        # Check if DRF pagination keys ('results', 'count', 'next') exist
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)