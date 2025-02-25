   from appointment2 import search_patient_by_name, search_practitioner_by_name, create_appointment

# Input the names for patient and practitioner.
patient_name = "Audra Thurs"  
 # Change to the desired patient name.
practitioner_name = "Amanda Miller"  # Change to the desired practitioner name.

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
    start_time = "2025-03-10T13:30:00.000Z"  # Set the desired start time.
    end_time = "2025-03-10T14:00:00.000Z"    # Set the desired end time.
    appointment_type_display = "Telemedicine"  # Options: Home Visit, Telemedicine, Office Visit, Lab Visit, Phone Call

    response = create_appointment(
        patient_id, practitioner_id, reason_text, start_time, end_time, appointment_type_display
    )

    print("Appointment creation response:")
    print("Status Code:", response["status_code"])
    print("Response Body:", response["response_body"])