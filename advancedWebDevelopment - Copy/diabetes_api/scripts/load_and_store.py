import os
import sys
import csv
import django
from datetime import datetime
from django.db import transaction  # Ensures database integrity with atomic operations

# ---------------------------------------------------------
# 1. SETUP DJANGO ENVIRONMENT
# ---------------------------------------------------------
# Identify the project root and add it to the system path for module discovery
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set the settings module (Ensure 'diabetes_api' matches your project folder name)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'diabetes_api.settings')
django.setup()

# Import the Admission model after Django has been initialized
from admissions.models import Admission

# ---------------------------------------------------------
# 2. DATA LOADING & CLEANING FUNCTION
# ---------------------------------------------------------
def load_data():
    """
    Performs an ETL (Extract, Transform, Load) process:
    1. Wipes existing data to ensure a fresh state.
    2. Cleans and standardizes categorical/numerical data from CSV.
    3. Uses Bulk Create and Transactions for high-performance database insertion.
    """
    csv_file_path = 'final_readmit_df.csv'

    # --- STEP 1: ERASE PREVIOUS DATA ---
    # Resets the table so running the script multiple times doesn't create duplicates.
    print("--- Erasing old database records ---")
    Admission.objects.all().delete()

    print(f"--- Starting data load from {csv_file_path} ---")

    # --- STEP 2: OPEN CSV AND INITIALIZE BATCHING ---
    try:
        with open(csv_file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            batch = []   # List to store objects in memory before bulk insertion
            count = 0    # Tracks successful record imports
            errors = 0   # Tracks skipped records due to formatting issues

            # --- STEP 3: ATOMIC TRANSACTION ---
            # transaction.atomic ensures that if the script crashes, 
            # the database doesn't end up with partial/corrupted data.
            with transaction.atomic():
                for row in reader:
                    try:
                        # --- DATA CLEANING & TRANSFORMATION ---
                        
                        # A. Standardize categorical strings to UPPERCASE for consistent API filtering
                        gender = row.get('sex', 'UNKNOWN').strip().upper()
                        race = row.get('race', 'UNKNOWN').strip().upper()
                        hba1c = row.get('HbA1c', 'NONE').strip().upper()
                        insulin = row.get('insulin_level', 'STEADY').strip().upper()
                        admit_source = row.get('admit_source', 'UNKNOWN').strip().upper()

                        # B. Age Cleaning: Remove 'years' and whitespace to leave clean tokens like '>60' or '<60'
                        raw_age = row.get('age', 'UNKNOWN').strip()
                        clean_age = raw_age.replace('years', '').replace(' ', '')

                        # C. Convert Boolean strings ('yes'/'no') to Python Booleans
                        is_med = row.get('diabetesMed', 'no').strip().lower() == 'yes'
                        is_readmitted = row.get('readmitted', 'no').strip().lower() == 'yes'

                        # D. Date transformation
                        raw_date = row.get('date', '2000-01-01')
                        date_obj = datetime.strptime(raw_date, '%Y-%m-%d').date()

                        # --- CREATE OBJECT IN MEMORY ---
                        # We build the objects in a list first to avoid hitting the DB 10,000+ times
                        admission = Admission(
                            admission_date=date_obj,
                            race=race,
                            sex=gender,
                            age_group=clean_age,
                            hospital_stay=int(row.get('hospital_stay', 0)),
                            hba1c=hba1c,
                            diabetes_med=is_med,
                            admit_source=admit_source,
                            patient_visits=int(row.get('patient_visits', 0)),
                            num_medications=int(row.get('num_medications', 0)),
                            num_diagnosis=int(row.get('num_diagnosis', 0)),
                            insulin_level=insulin,
                            readmitted=is_readmitted
                        )
                        
                        batch.append(admission)
                        count += 1

                        # --- STEP 4: BULK INSERTION ---
                        # Instead of 1,000 separate INSERT queries, we perform 1 query per 1,000 rows.
                        # This significantly improves performance on large datasets.
                        if len(batch) >= 1000:
                            Admission.objects.bulk_create(batch)
                            batch = [] # Reset the list after pushing to DB
                            print(f"Progress: {count} records loaded...")

                    except Exception as e:
                        errors += 1
                        # Log error and skip row to ensure the rest of the file is processed
                        continue 

                # Final push for any remaining records in the list
                if batch:
                    Admission.objects.bulk_create(batch)

        print("-" * 30)
        print(f"SUCCESS: {count} records loaded.")
        print(f"SKIPPED: {errors} records due to formatting errors.")
        print("-" * 30)

    except FileNotFoundError:
        print(f"ERROR: Could not find {csv_file_path}. Ensure it is in the root project folder.")

# ---------------------------------------------------------
# 3. RUN SCRIPT
# ---------------------------------------------------------
if __name__ == "__main__":
    load_data()