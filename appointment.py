import requests
import os

XPC_API_KEY = os.environ.get("XPC_API_KEY")
XPC_FHIR_API_BASE_URL = os.environ.get("XPC_FHIR_API_BASE_URL")
patient_url = XPC_FHIR_API_BASE_URL.rstrip('/') + '/Appointment'


def create_appointment(status, display):
    headers = {
        'Authorization': f'Bearer {XPC_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "resource": {
            "resourceType":
            "Appointment",
            "status":
            status,
            "appointmentType": {
                "coding": [{
                    "system":
                    "http://snomed.info/sct",
                    "code":
                    "448337001",
                    "display":
                    display
                }]
            },
            "description":
            "Weekly check-in.",
            "supportingInformation": [{
                "reference": "Location/1"
            }],
            "start":
            "2025-01-21T13:30:00.000Z",
            "end":
            "2025-01-21T14:00:00.000Z",
            "participant": [{
                "actor": {
                    "reference":
                    "Practitioner/9b31de0f2040478e94e4f9b9b409bce0"
                },
                "status": "accepted"
            }, {
                "actor": {
                    "reference": "Patient/2f9ad84fdf2842ccac1a11594904c2b4"
                },
                "status": "accepted"
            }]
        }
    }
    response = requests.post(patient_url, headers=headers, json=payload)

    # Optionally, inspect the response
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)


# print URL with patient key in response header
