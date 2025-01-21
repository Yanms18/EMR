import requests
from datetime import date
import os

XPC_API_KEY = os.environ.get("XPC_API_KEY")
XPC_FHIR_API_BASE_URL = os.environ.get("XPC_FHIR_API_BASE_URL")
patient_url = XPC_FHIR_API_BASE_URL.rstrip('/') + '/Patient'


def age_to_iso_birthday_fixed(age):
    year = date.today().year - age
    approx_birthday = date(year, 1, 1)  # Always January 1
    return approx_birthday.isoformat()


def create_patient0(firstname, lastname, age, sex, gender):
    if sex not in ("F", "M", "OTH", "UNK"):
        raise ValueError(f"Sex {sex} is invalid")
    if gender not in ("female", "male", "other", "unknown"):
        raise ValueError(f"Gender {gender} is invalid")
    headers = {
        'Authorization': f'Bearer {XPC_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "resourceType":
        "Patient",
        "extension": [{
            "url":
            "http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex",
            "valueCode": sex
        }],
        "gender":
        gender,
        "active":
        True,
        "name": [{
            "use": "official",
            "family": lastname,
            "given": [firstname]
        }],
        "birthDate":
        age_to_iso_birthday_fixed(age)
    }
    data = {
        "resource": {
            "resourceType": "Appointment",
            "status": "booked",
            "appointmentType": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "448337001",
                        "display": "Telemedicine consultation with patient (procedure)"
                    }
                ]
            },
            "description": "Weekly check-in.",
            "supportingInformation": [
                {
                    "reference": "Location/1"
                }
            ],
            "start": "2025-01-21T13:30:00.000Z",
            "end": "2025-01-21T14:00:00.000Z",
            "participant": [
                {
                    "actor": {
                        "reference": "Practitioner/9b31de0f2040478e94e4f9b9b409bce0>"
                    },
                    "status": "accepted"
                },
                {
                    "actor": {
                        "reference": "Patient/2f9ad84fdf2842ccac1a11594904c2b4"
                    },
                    "status": "accepted"
                }
            ]
        }
    response = requests.post(patient_url, headers=headers, json=payload)

    # Optionally, inspect the response
    print("Status Code:", response.status_code)
    print("Response Body:", response.text)


# print URL with patient key in response header
