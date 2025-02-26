from appointment import search_patient_by_name, search_practitioner_by_name, create_appointment
from datetime import datetime, timedelta

# Input the names for patient and practitioner.
patient_name = "Audra Thurs"  
practitioner_name = "Amanda Miller"

# Input the appointment date and time
appointment_date = "2025-03-10"  # YYYY-MM-DD format
appointment_time = "13:30:00"    # HH:MM:SS format

# Combine date and time into a single datetime object
start_datetime = datetime.strptime(f"{appointment_date}T{appointment_time}", "%Y-%m-%dT%H:%M:%S")

# Calculate end time by adding 1 hour to start time
end_datetime = start_datetime + timedelta(hours=1)

# Format start and end times in the required format
start_time = start_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")
end_time = end_datetime.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# Search for the patient and practitioner IDs based on their names.
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

# If both IDs are found, proceed to create the appointment.
if patient_id and practitioner_id:
    reason_text = "Urgent Visit"
    appointment_type_display = "Telemedicine"  # Options: Home Visit, Telemedicine, Office Visit, Lab Visit, Phone Call

    response = create_appointment(
        patient_id, practitioner_id, reason_text, start_time, end_time, appointment_type_display
    )

    print("Appointment creation response:")
    print("Status Code:", response["status_code"])
    print("Response Body:", response["response_body"])