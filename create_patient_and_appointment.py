from patient0 import create_patient0
from appointment import search_patient_by_name, search_practitioner_by_name, create_appointment
from datetime import datetime, timedelta
import os

# Verify that the API key and base URL are loaded
XPC_API_KEY = os.environ.get("XPC_API_KEY")
XPC_FHIR_API_BASE_URL = os.environ.get("XPC_FHIR_API_BASE_URL")


# Input the patient details
firstname = "John"
lastname = "titor"
age = 97
sex = "M"  # Options: F, M, OTH, UNK
gender = "male"  # Options: female, male, other, unknown

# Create patient
patient_response = create_patient0(firstname, lastname, age, sex, gender)

# Input the appointment details
patient_name = f"{firstname} {lastname}"
practitioner_name = "Amanda Miller"
appointment_date = "2025-03-10"  # YYYY-MM-DD format
appointment_time = "13:30:00"    # HH:MM:SS format
reason_text = "Urgent Visit"
appointment_type_display = "Home Visit"  # Options: Home Visit, Telemedicine, Office Visit, Lab Visit, Phone Call

# Combine date and time into a single datetime object
start_datetime = datetime.strptime(f"{appointment_date}T{appointment_time}", "%Y-%m-%dT%H:%M:%S")

# Calculate end time by adding 1 hour to start time
end_datetime = start_datetime + timedelta(hours=1)

# Format start and end times in the required format
start_time = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
end_time = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# Search for the practitioner ID based on their name
try:
    patient_id = search_patient_by_name(patient_name)
    print(f"Found patient ID: {patient_id} for patient name: {patient_name}")
except Exception as e:
    print(f"Error finding patient: {e}")
    patient_id = None


try:
    practitioner_id = search_practitioner_by_name(practitioner_name)
    print(f"Found practitioner ID: {practitioner_id} for practitioner name: {practitioner_name}")
except Exception as e:
    print(f"Error finding practitioner: {e}")
    practitioner_id = None

if not practitioner_id:
    raise ValueError("Failed to find practitioner. No practitioner ID returned.")

# Create appointment
appointment_response = create_appointment(
    patient_id, practitioner_id, reason_text, start_time, end_time, appointment_type_display
)

print("Appointment creation response:")
print("Status Code:", appointment_response["status_code"])
print("Response Body:", appointment_response["response_body"])