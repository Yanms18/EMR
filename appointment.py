import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


XPC_API_KEY = os.getenv('XPC_API_KEY')
XPC_FHIR_API_BASE_URL = os.getenv('XPC_FHIR_API_BASE_URL')

# Print the loaded environment variables for debugging
# print(f"XPC_API_KEY: {XPC_API_KEY}")
# print(f"XPC_FHIR_API_BASE_URL: {XPC_FHIR_API_BASE_URL}")


# Base URLs for each FHIR resource
APPOINTMENT_URL = XPC_FHIR_API_BASE_URL.rstrip('/') + '/Appointment'
PATIENT_URL = XPC_FHIR_API_BASE_URL.rstrip('/') + '/Patient'
PRACTITIONER_URL = XPC_FHIR_API_BASE_URL.rstrip('/') + '/Practitioner'

# Mapping for appointment types: Display -> Code
APPOINTMENT_TYPE_MAP = {
    "Home Visit": "439708006",
    "Telemedicine": "448337001",
    "Office Visit": "308335008",
    "Lab Visit": "31108002",
    "Phone Call": "185317003"
}

def create_appointment(patient_id, practitioner_id, reason_text, start_time, end_time, appointment_type_display):
    """
    Create an appointment using the provided IDs and details.
    """
    if appointment_type_display not in APPOINTMENT_TYPE_MAP:
        raise ValueError(
            f"Invalid appointment type: {appointment_type_display}. "
            f"Valid types are: {list(APPOINTMENT_TYPE_MAP.keys())}"
        )
<<<<<<< HEAD
    
    appointment_type_code = APPOINTMENT_TYPE_MAP[appointment_type_display]
    
=======

    appointment_type_code = APPOINTMENT_TYPE_MAP[appointment_type_display]

>>>>>>> 1488e6d3eb876b58aaaa28400b2d25045fd31f04
    headers = {
        "Authorization": f"Bearer {XPC_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
<<<<<<< HEAD
    
=======

>>>>>>> 1488e6d3eb876b58aaaa28400b2d25045fd31f04
    payload = {
        "resourceType": "Appointment",
        "reasonCode": [{
            "coding": [{
                "system": "INTERNAL",
                "display": reason_text
            }],
            "text": reason_text
        }],
        "participant": [
            {
                "actor": {"reference": f"Patient/{patient_id}"},
                "status": "accepted"
            },
            {
                "actor": {"reference": f"Practitioner/{practitioner_id}"},
                "status": "accepted"
            }
        ],
        "appointmentType": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": appointment_type_code,
                "display": appointment_type_display
            }]
        },
        "start": start_time,
        "end": end_time,"supportingInformation": [
        { "reference": "Location/1"}],
        "status": "proposed"
    }
<<<<<<< HEAD
    
    response = requests.post(APPOINTMENT_URL, headers=headers, json=payload)
    
=======

    response = requests.post(APPOINTMENT_URL, headers=headers, json=payload)

>>>>>>> 1488e6d3eb876b58aaaa28400b2d25045fd31f04
    return {
        "status_code": response.status_code,
        "response_body": response.text
    }

def search_patient_by_name(patient_name):
    """
    Search for a patient by name and return the first matching patient ID.
    """
    headers = {
        "Authorization": f"Bearer {XPC_API_KEY}",
        "Accept": "application/json"
    }
    # FHIR search using the 'name' parameter
    params = {"name": patient_name}
    response = requests.get(PATIENT_URL, headers=headers, params=params)
<<<<<<< HEAD
    
    if response.status_code != 200:
        raise Exception(f"Error searching patient: {response.status_code} {response.text}")
    
    data = response.json()
    if data.get("total", 0) == 0 or "entry" not in data:
        raise Exception(f"No patient found with name '{patient_name}'")
    
=======

    if response.status_code != 200:
        raise Exception(f"Error searching patient: {response.status_code} {response.text}")

    data = response.json()
    if data.get("total", 0) == 0 or "entry" not in data:
        raise Exception(f"No patient found with name '{patient_name}'")

>>>>>>> 1488e6d3eb876b58aaaa28400b2d25045fd31f04
    # Extract and return the patient id from the first entry
    patient_id = data["entry"][0]["resource"]["id"]
    return patient_id

def search_practitioner_by_name(practitioner_name):
    """
    Search for a practitioner by name and return the first matching practitioner ID.
    """
    headers = {
        "Authorization": f"Bearer {XPC_API_KEY}",
        "Accept": "application/json"
    }
    # FHIR search using the 'name' parameter
    params = {"name": practitioner_name}
    response = requests.get(PRACTITIONER_URL, headers=headers, params=params)
<<<<<<< HEAD
    
    if response.status_code != 200:
        raise Exception(f"Error searching practitioner: {response.status_code} {response.text}")
    
    data = response.json()
    if data.get("total", 0) == 0 or "entry" not in data:
        raise Exception(f"No practitioner found with name '{practitioner_name}'")
    
=======

    if response.status_code != 200:
        raise Exception(f"Error searching practitioner: {response.status_code} {response.text}")

    data = response.json()
    if data.get("total", 0) == 0 or "entry" not in data:
        raise Exception(f"No practitioner found with name '{practitioner_name}'")

>>>>>>> 1488e6d3eb876b58aaaa28400b2d25045fd31f04
    # Extract and return the practitioner id from the first entry
    practitioner_id = data["entry"][0]["resource"]["id"]
    return practitioner_id