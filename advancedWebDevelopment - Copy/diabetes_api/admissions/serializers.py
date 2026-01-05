
from rest_framework import serializers
from .models import Admission

class AdmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admission
        # List all fields you want exposed via the API
        fields = [
            'id',             
            'admission_date',
            'race',
            'sex',
            'age_group',
            'hospital_stay',
            'hba1c',
            'diabetes_med',
            'admit_source',
            'patient_visits',
            'num_medications',
            'num_diagnosis',
            'insulin_level',
            'readmitted'
        ]
