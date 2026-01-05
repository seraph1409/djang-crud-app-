from django.db import models

class Admission(models.Model):
    admission_date = models.DateField()
    race = models.CharField(max_length=20)
    sex = models.CharField(max_length=10)
    age_group = models.CharField(max_length=20)

    hospital_stay = models.IntegerField()

    hba1c = models.CharField(max_length=20)
    diabetes_med = models.BooleanField()

    admit_source = models.CharField(max_length=20)

    patient_visits = models.IntegerField()
    num_medications = models.IntegerField()
    num_diagnosis = models.IntegerField()

    insulin_level = models.CharField(max_length=20)
    readmitted = models.BooleanField()

    def __str__(self):
        return f"{self.sex} | {self.age_group} | {self.admission_date}"
