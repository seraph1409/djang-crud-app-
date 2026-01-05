import factory
from .models import Admission

class AdmissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Admission

    admission_date = '2023-01-01'
    race = 'Caucasian'
    sex = 'MALE'
    age_group = '>=60'
    hospital_stay = 5
    hba1c = 'ELEVATED'
    diabetes_med = True
    admit_source = 'Emergency'
    patient_visits = 1
    num_medications = 10
    num_diagnosis = 5
    insulin_level = 'STEADY'
    readmitted = False